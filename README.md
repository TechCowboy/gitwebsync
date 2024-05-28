# gitwebsync

This python script is not an example of good code, but it does the job

Near the top of the file is the variable 'account' -- set it to your github account

This is what it does

Part one:
1) Starts a selenium session and minimizes browser
2) Find all the github repositories for the specified account
3) Checks to see if a repository is forked. if not goes to next repository
4) Checks to see if we are ahead -- if so, goes to next repository
5) Checks to see if there are missing commits, then performs a web sync

Part two:
1) Finds all the local repositories
2) Determines the status of the local repositories
3) Syncs where possible
 
