import {defineConfig,devices} from '@playwright/test';
export default defineConfig({
  testDir:'./tests',fullyParallel:false,workers:1,timeout:120000,
  use:{baseURL:'http://127.0.0.1:4173/null-city/',trace:'retain-on-failure',
    launchOptions:{...(process.env.PW_USE_CHROME?{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{}),args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}},
  projects:[{name:'desktop',use:{viewport:{width:1440,height:1000}}},{name:'mobile',use:{...devices['iPhone 13'],defaultBrowserType:'chromium',...(process.env.CI?{deviceScaleFactor:1}:{})}}],
  webServer:{command:'npm run preview -- --host 127.0.0.1 --port 4173 --base /null-city/',url:'http://127.0.0.1:4173/null-city/',reuseExistingServer:!process.env.CI},
});
