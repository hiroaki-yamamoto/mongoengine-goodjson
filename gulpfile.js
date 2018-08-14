'use strict';
const gulp = require('gulp');
const rimraf = require('rimraf');


const createRimRafPromise = (path) => {
  return new Promise((res, rej) => {
    rimraf(
      path,
      (err) => {
        if (err) { return rej(err); }
        return res();
      }
    );
  });
};


gulp.task('clean', () => {
  const pyCachePromise = createRimRafPromise('!(venv|.tox)/__pycache__');
  const pycoPromise = createRimRafPromise(
    '!(__pycache__|venv|\.tox)/**/**.py[co]'
  );
  const eggInfoPromise = createRimRafPromise('mongoengine_goodjson.egg-info');
  const toxPromise = createRimRafPromise('.tox');
  return Promise.all([
    toxPromise,
    pyCachePromise,
    pycoPromise,
    eggInfoPromise
  ]);
});
