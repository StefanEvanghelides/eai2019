const webpack = require('webpack')
const Dotenv = require('dotenv-webpack')

module.exports = {
  entry: './src/client.js',
  output: {
    path: __dirname + '/dist',
    filename: 'bundle.js',
  },
  plugins: [
  	new Dotenv()
  ]
}
