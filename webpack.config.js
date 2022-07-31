module.exports = {
  entry: "./src/index.ts",
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
  output: {
    filename: "sql-httpvfs.js",
    library: {
      type: "module" // output a JavaScript module
    },
    module: true, // truly
  },
  experiments: {
    outputModule: true  // yes, we really want one
  },
  optimization: {
    minimize: true
  },
};
