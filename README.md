scifiweb
========

The main website for Project SCIFI.


## Developers' guide


### Getting the source

Clone the repo and check out submodules:
```
git clone https://github.com:project-scifi/scifiweb.git
git submodule update --init
```
If you get scss import errors, it's because you haven't run the second command.


### Running in development mode

Run `make dev`. The first run will build a virtualenv and may take longer than
subsequent runs. You can visit the website at `0.0.0.0:8000` or
`<hostname>:8000`.

The development server will automatically reload whenever you make changes, so
you can leave it running while you work on the website.


### Building SCSS

If you change the scss while the dev server is running, you will have to
rebuild it by running `make scss`. You can continuously rebuild it by running
`watch make scss`.


### Running tests

To run tests locally, run `make test`. It's good to be in the habit of doing
this before each push.


### Running pre-commit

[Pre-commit](http://pre-commit.com/) automatically checks code for style and
syntax errors before making a commit. Most of the time, it will even make
corrections for you, which gets consistent style without much effort.

You can run `make install-hooks` to install pre-commit to your local git repo.
Once installed, pre-commit will run every time you commit.

Alternatively, if you'd rather not install any hooks, you can simply use `make
test` as usual, which will also run the hooks.


### Installing packages

To install a package to the production environment, add it to
`requirements-minimal.txt`, then run `make update-requirements`. Similarly, to
install to the development environment, add to `requirements-dev-minimal.txt`
and run `make upgrade-requirements`. Use as loose a version requirement as
possible, e.g. try `django` or `django>=1.10,<1.10.999` before
`django==1.10.0`.


-----

`scifiweb` has used code from:
* [ocfweb](https://github.com/ocf/ocfweb)
* [startbootstrap-creative](https://github.com/BlackrockDigital/startbootstrap-creative)

See the associated repositories for the license under which their code is used.
