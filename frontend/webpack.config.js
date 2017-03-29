var path = require('path');
var webpack = require('webpack');
var webpackMerge = require('webpack-merge');
var fs = require('fs');

function getDjangoSettings() {
  var ds = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'djangoSettings.json'), 'utf8'));

  for (var k in ds) {
    if (ds.hasOwnProperty(k)) {
      if (typeof(ds[k] === 'string')) {
        ds[k] = '"' + ds[k] + '"';
      }
    }
  }
  return ds;
}

var djangoSettings = getDjangoSettings();

var baseConfig = {
  output: {
    path: path.resolve(__dirname, "dist/webpack"),
    filename: '[name].bundle.js',
    publicPath: "/static/webpack/"
  },
  devtool: "#source-map",
  module: {
    rules: [
      // Much of this is from https://medium.com/@victorleungtw/how-to-use-webpack-with-react-and-bootstrap-b94d33765970#.71y0p3y0c
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules|bower_components)/,
        loader: 'babel-loader',
        options: {
          presets: ['es2015', 'react', 'stage-2']
        }
      },
      { 
        test: /\.css$/, 
        use: [
          "style-loader",
          "css-loader"
        ]
      },
      { 
        test: /\.png$/, 
        loader: "url-loader?limit=100000" 
      },
      { 
        test: /\.jpg$/, 
        loader: "file-loader" 
      },
      {
        test: /\.(woff|woff2)(\?v=\d+\.\d+\.\d+)?$/, 
        loader: 'url-loader?limit=10000&mimetype=application/font-woff'
      },
      {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, 
        loader: 'url-loader?limit=10000&mimetype=application/octet-stream'
      },
      {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, 
        loader: 'file-loader'
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, 
        loader: 'url-loader?limit=10000&mimetype=image/svg+xml'
      }
      // ,
      // {
      //   test: require.resolve('bootstrap/dist/js/bootstrap.js'),
      //   loader: 'imports-loader?jQuery=jquery'
      // }
    ]
  },
  plugins: [
//    new webpack.optimize.UglifyJsPlugin({minimize: true, sourceMap: true})
    new webpack.NamedModulesPlugin(),
    new webpack.DefinePlugin({
      DJANGO_SETTINGS:djangoSettings
    })
  ]
  // plugins: [
  //   new webpack.optimize.CommonsChunkPlugin({
  //     name: 'inline',
  //     filename: 'inline.js',
  //     minChunks: Infinity
  //   }),
  //   new webpack.optimize.AggressiveSplittingPlugin({
  //       minSize: 5000,
  //       maxSize: 10000
  //   }),
  // ]
};

var targets = [
  // webpackMerge(baseConfig, {
  //   entry: './src/models.js',
  //   output: {
  //     filename: 'models.bundle.js',
  //     library: "models"
  //   }
  // }),
  
  webpackMerge(baseConfig, {
    entry: './src/portal/portal.jsx',
    output: {
      filename: 'portal.bundle.js',
      library: "portal"
    },
    resolve: {
      modules: [
	path.resolve(__dirname, 'src'),
	path.resolve(__dirname, 'src/portal'),
	path.resolve(__dirname, 'src/portal/pages'),
	path.resolve(__dirname, 'src/portal/components'),
	path.resolve(__dirname, 'src/shared/components'),
	path.resolve(__dirname, 'node_modules')
      ],
      extensions: ['.js', '.jsx']
    }
    
  }),
  
  webpackMerge(baseConfig, {
    entry: './src/lms/lms.jsx',
    output: {
      filename: 'lms.bundle.js',
      library: "lms"
    },
    resolve: {
      modules: [
	path.resolve(__dirname, 'src'),
	path.resolve(__dirname, 'src/lms'),
	path.resolve(__dirname, 'src/lms/pages'),
	path.resolve(__dirname, 'src/lms/components'),
	path.resolve(__dirname, 'src/shared/components'),
	path.resolve(__dirname, 'node_modules')
      ],
      extensions: ['.js', '.jsx']
    }
  })
];

module.exports = targets;

////////////////////////////////////////////////////////////////////////////////

