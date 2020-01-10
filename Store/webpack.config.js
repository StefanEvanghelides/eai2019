const webpack = require('webpack')


module.exports = {
  entry: './src/client.js',
  output: {
    path: __dirname + '/dist',
    filename: 'bundle.js',
  },
}
