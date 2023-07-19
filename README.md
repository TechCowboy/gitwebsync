# gitwebsync

This python script is not an example of good code, but it does the job

Near the top of the file is the variable 'account' -- set it to your github account

This is what it does

1) Starts a selenium session and minimizes browser
2) Find all the github repositories for the specified account
3) Determines which repositories are a fork and need syncing
4) Maximizes browser and then performs a web sync on each out-of-date repository
5) Finds all the local repositories
6) Determines the status of the local repositories
7) Syncs where possible
 
