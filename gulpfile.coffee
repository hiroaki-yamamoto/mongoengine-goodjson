g = require "gulp"
notify = require "gulp-notify"
childProcess = require "child_process"
q = require "q"

g.task "test", ->
  testCommand = [
    "nosetests"
    "--with-coverage"
    "--cover-erase"
    "--cover-package=mongoengine_goodjson"
    "--all tests"
  ]
  commands = [
    "echo 'PEP8 Syntax...'"
    "flake8 mongoengine_goodjson tests"
    "echo 'Code Metrics...'"
    "radon cc -nc mongoengine_goodjson"
    "echo 'Maintenancibility...'"
    "radon mi -nc mongoengine_goodjson"
    "echo 'Unit testing...'"
    testCommand.join " "
  ]
  if not process.env.CI
    commands.splice 0, 0, ". ../bin/activate"
    commands.push "deactivate"
  commands = commands.join ("&&")
  defer = q.defer()
  child = childProcess.exec commands
  child.stdout.pipe process.stdout
  child.stderr.pipe process.stderr
  child.on "error", (error) ->
    notify.onError("<%= error.message %>")(error)
    defer.reject(error)
  child.on "close", (code, signal) ->
    errStr = "The command failed with "
    if code isnt null and code > 0
      codeErr = errStr + " code: #{code}"
      notify.onError("<%= error.message %>")(new Error codeErr)
      defer.reject codeErr
      return
    if signal isnt null
      codeErr = errStr + " signal: #{signal}"
      notify.onError("<%= error.message %>")(new Error codeErr)
      defer.reject codeErr
      return
    defer.resolve()
  defer.promise

g.task "default", ->
  g.watch [
    "mongoengine_goodjson/**/*.py"
    "tests/**/*.py"
  ], ["test"]
