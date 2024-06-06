# Introduction
Aptly-manage is a tool developed for organizations that use [aptly](https://aptly.info) to host and manange a private
package / distribution mirror.

The aptly tool allows organizations to control which environment (DTAP) will receive certain updates and when.
This allows organizations to deploy patches in a controlled manner, such that patches are properly tested before
applied to production.

Because using the aptly tool itself can become a lot of manual work, the aptly-manage tool has been developed.
Aptly-manage, uses aptly under-the-hood to create & update multiple mirrors, create snapshots for all mirrors
and publishes those snapshots for multiple targets.

# Prerequisites

- You must have aptly already installed and configured, including gpg signing key

# Installation

1. Create a user called 'aptly'
2. Copy the 'aptly-manage' folder to the home directory
3. Copy [the configuration file](config/mirrorlist.yaml.example) into 'mirrorlist.yaml' in the /home/aptly directory.
4. Edit the configuration file as you see fit.

# Usage

In the examples below, a command and action operate on all mirrors sequentially.
The example also demonstrates how to use the 'aptly publish switch' command to swap old
snapshots with new ones, without tearing down the published endpoints.

```
./aptly-manage --command mirror --action create
./aptly-manage --command mirror --action update
./aptly-manage --command snapshot --action create --tag feb01
./aptly-manage --command publish --action snapshot --tag feb01 --target test --date 2024-02-01
./aptly-manage --command snapshot --action create --tag feb02
./aptly-manage --command publish --action switch --tag feb02 --target test --date 2024-02-02
./aptly-manage --command snapshot --action drop --tag feb01
```
