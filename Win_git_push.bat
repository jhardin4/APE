set /p commes="Enter commit message:"
call git add -A
call git commit -m "%commes%"
call git push google master