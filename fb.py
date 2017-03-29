# -*- coding: utf-8 -*-

from lp.models import User, UserInvite, FacebookProfile

# Django
from django.conf import settings
from django.utils import timezone, dateparse

# External dependencies
import facebook
import requests

# Standard stuff
import datetime
import logging
logger = logging.getLogger(__name__)

# ES: Commented out some unused stuff.

# def get_access_token_from_code(app_id, app_secret):           
#     payload = {'grant_type': 'client_credentials', 'client_id': app_id, 'client_secret': app_secret}
#     file = requests.post('https://graph.facebook.com/oauth/access_token?', params = payload)
#     #print file.text #to test what the FB api responded with    
#     result = file.text.split("=")[1]
#     #print file.text #to test the TOKEN
#     return result


# def fb_login(request):
#     '''
#     Facebook login call by the client-side API. Client must first log in using
#     the Facebook JavaScript SDK, with the `cookie` parameter set, like so:

#     ````
#     FB.init({
#       appId   : '{your-app-id}',
#       cookie  : true,
#       version : 'v2.2'
#     });
#     ````

#     When that parameter is present, Facebook's JavaScript code will set a cookie
#     called fbsr_{your-app-id} that contains a `signed_request` as documented at
#     https://developers.facebook.com/docs/reference/login/signed-request/

#     From that we can extract a code, which we use to get an access token.
#     '''

#     try:
#         cookie = request.COOKIES["fbsr_" + settings.FACEBOOK_APP_ID]
#     except KeyError:
#         logger.debug('facebook_login: no cookie')
#         logout(request)
#         raise AuthenticationFailed # From REST framework

def access_token_is_valid(access_token, fbid):
        try:
            token_info = facebook.GraphAPI().debug_access_token(access_token,
                                                                settings.FACEBOOK_APP_ID,
                                                                settings.FACEBOOK_APP_SECRET)
            if not token_info['data']['is_valid'] or \
               token_info['data']['app_id'] != settings.FACEBOOK_APP_ID or \
                                               token_info['data']['user_id'] != fbid:
                logger.error('access_token_is_valid: FB says access_token %s is invalid', access_token)
                return False
        except (facebook.GraphAPIError, KeyError) as ex:
            logger.exception('Could not verify access token %s', access_token)
            return False
        return True
    
class FacebookAccessTokenBackend:
    def authenticate(self, fbid, access_token, expiration_date, invite_code=None):
        logger.debug('FacebookAccessTokenBackend:authenticate: %s, %s, %s', fbid, access_token, expiration_date)
        # Check the expiration date. Parse specifies the format yyyy-MM-dd'T'HH:mm:ss.SSS'Z'
        try:
            expires = dateparse.parse_datetime(expiration_date)
        except ValueError:
            logger.warning('FacebookAccessTokenBackend: Invalid expires date.')
            return None

        # Verify the access token.
        if not access_token_is_valid(access_token, fbid):
            return None

        # Try to extend the access token.
        # ES: Not really necessary with this app.
        # graph = facebook.GraphAPI(access_token)
        # try:
        #     at_result = graph.extend_access_token(settings.FACEBOOK_APP_ID,
        #                                           settings.FACEBOOK_APP_SECRET)
        #     access_token = at_result['access_token']
        #     expires_in = at_result.get('expires')
        #     expires = # ES: FILL IN
        #     logger.debug('facebook_login: extended access token %s to %s', access_token, expires)
        # except facebook.GraphAPIError as ex:
        #     logger.warning('FacebookBackend: could not extend access token: %s', ex)
        #     # Not fatal.

        try:
            user = User.objects.get(facebook_profile__facebook_id=fbid)
            profile,_created = FacebookProfile.objects.get_or_create(facebook_id=fbid,
                                                                     user=user)
            profile.access_token = access_token
            profile.access_token_expires = expires
            profile.save()
            return user
        except User.DoesNotExist:
            try:
                invite = UserInvite.objects.get_from_invite_code(invite_code)
                user = invite.user
            except UserInvite.DoesNotExist:
                # Users can't create accounts unless they have an invite code.
                logger.warning('FacebookBackend: No user and no invite code')
                return None
            invite.delete()
            profile = FacebookProfile.objects.create(facebook_id=fbid,
                                                     user=user,
                                                     access_token=access_token,
                                                     access_token_expires=expires)
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        

# class FacebookSignedRequestBackend(object):
#     '''
#     Authenticate against FaceBook.
#     '''

#     def authenticate(self, signed_request, invite_code=None):
#         logger.debug('FacebookBackend:authenticate: %s, %s', signed_request, invite_code)
#         parsed_request = facebook.parse_signed_request(signed_request, settings.FACEBOOK_APP_SECRET)
#         if not parsed_request:
#             logger.warning('FacebookBackend: Failed to parse signed_request')
#             return None

#         try:
#             user_id = parsed_request["user_id"]
#         except KeyError:
#             logger.warning('FacebookBackend: signed request has no user_id.')
#             return None

#         # Check the expiration date.
#         try:
#             expires_timestamp = int(parsed_request.get('expires'))
#         except (KeyError, ValueError):
#             logger.warning('FacebookBackend: signed request has no expires.')
#             return None
#         expires = timezone.now() + datetime.timedelta(seconds=int(expires_timestamp))

#         # Look for a provided oauth token
#         try:
#             access_token = parsed_request['oauth_token']
#             logger.debug('facebook_login: token from cookie')
#         except KeyError:
#             # No oauth token. Try to get one from the `code`.
#             try:
#                 code = parsed_request['code']
#             except KeyError:
#                 logger.warning('FacebookBackend: No oauth_token and no code')
#                 return None
#             try:
#                 access_token = facebook.GraphAPI().get_access_token_from_code(code, "",
#                                                                               settings.FACEBOOK_APP_ID,
#                                                                               settings.FACEBOOK_APP_SECRET)['access_token']
#             except (KeyError, facebook.GraphAPIError) as ex:
#                 logger.exception('FacebookBackend: No access token')
#                 return None
#             # Try to extend the access token.
#             graph = facebook.GraphAPI(access_token)
#             try:
#                 at_result = graph.extend_access_token(settings.FACEBOOK_APP_ID,
#                                                       settings.FACEBOOK_APP_SECRET)
#                 access_token = at_result['access_token']
#                 expires = at_result.get('expires')
#                 logger.debug('facebook_login: extended access token %s to %s', access_token, expires)
#             except facebook.GraphAPIError as ex:
#                 logger.warning('FacebookBackend: could not extend access token: %s', ex)
#                 # Not fatal.

#         # If we get here, we have an access_token and a user id.
#         try:
#             user = User.objects.get(facebook_profile__facebook_id=user_id)
#             profile,_created = FacebookProfile.objects.get_or_create(facebook_id=user_id,
#                                                                      user=user)
#             profile.access_token = access_token
#             profile.access_token_expires = expires
#             profile.save()
#             return user
#         except User.DoesNotExist:
#             try:
#                 user = User.objects.get_from_invite_code(invite_code)
#             except User.DoesNotExist:
#                 # Users can't create accounts unless they have an invite code.
#                 logger.warning('FacebookBackend: No user and no invite code')
#                 return None
                
#             profile = FacebookProfile.objects.create(facebook_id=user_id,
#                                                      user=user,
#                                                      access_token=access_token,
#                                                      access_token_expires=expires)
#             return user

#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None

    
