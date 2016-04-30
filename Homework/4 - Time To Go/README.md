Subcategory: Reversing

Can you reverse this binary and get the flag?

Binary is running on ssl-added-and-removed-here.ctfcompetition.com:8034 --
you'll need to account for the use of SSL when communicating with the server
:-)

The binary was compiled with GOROOT=/opt/go1.6 GOOS=linux GOARCH=arm GOARM=6
/opt/go1.6/bin/go build -ldflags="-s"
