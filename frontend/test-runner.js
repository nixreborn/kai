const { run } = require('jest');

run([
  '--config=jest.config.js',
  '--ci',
  '--passWithNoTests',
  '--maxWorkers=2',
  '--no-cache'
]);
