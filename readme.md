Milky Way Idle Market API
=========================

[Viewer](https://holychikenz.github.io/MWIApi/)

`marketapi.json` is the current market information  
`market.db` is the historical market information (sqlite)  
`medianmarket.json` running 24-hour median of ask and mid  

Building Viewer
---------------
Follow instructions from github.com/phiresky/sql.js-httpvfs
```sh
echo '{}' > package.json
npm install --save-dev webpack webpack-cli typescript ts-loader
npm install --save sql.js-httpvfs
npx tsc --init
```
Edit tsconfig.json
```json
"target": "es2020",
"module": "es2020",
"moduleResolution": "node",
```
Build the webpack
```
./node_modules/.bin/webpack --mode=production
```
