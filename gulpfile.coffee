require "colors"
g = require "gulp"
notify = require "gulp-notify"
childProcess = require "child_process"
q = require "q"
rimraf = require "rimraf"

g.task "test", ->
  spawnInEnv = (command) ->
    defer= q.defer()
    if command not instanceof Array
      command = [command]
    if not process.env.CI
      command.splice 0, 0, ". ../bin/activate"
      command.push "deactivate"
    command = command.join "&&"
    child = childProcess.spawn command, [], (
      "shell": true,
      "stdio": "inherit"
    )
    child.on "error", (error) ->
      notify.onError("<%= error.message %>")(error)
      defer.reject error
    child.on "close", (code, signal) ->
      errStr = "The command failed with "
      if code isnt null and code > 0
        codeErr = new Error errStr + " code: #{code}"
        notify.onError("<%= error.message %>")(codeErr)
        defer.reject codeErr
      if signal isnt null
        signalErr = new Error errStr + " signal: #{signal}"
        notify.onError("<%= error.message %>")(signalErr)
        defer.reject signalErr
      defer.resolve()
    defer.promise
  q.fcall(
    ->
      console.log ("Cheking PEP8 Syntax...").green
      spawnInEnv "flake8 mongoengine_goodjson tests"
  ).then(
    ->
      console.log ("Checking Code Metrics...").green
      spawnInEnv "radon cc -nc mongoengine_goodjson"
  ).then(
    ->
      console.log ("Chekcing Maintenancibility...").green
      spawnInEnv "radon mi -nc mongoengine_goodjson"
  ).then(
    ->
      console.log ("Unit testing...").green
      spawnInEnv "nosetests --with-coverage --cover-erase --cover-package=mongoengine_goodjson --all tests"
  )

g.task "clean", ->
  q.all [
    q.nfcall rimraf, "**/__pycache__"
    q.nfcall rimraf, "!(__pycache__)/**.pyc"
  ]

g.task "default", ->
  g.watch [
    "mongoengine_goodjson/**/*.py"
    "tests/**/*.py"
  ], ["test"]
