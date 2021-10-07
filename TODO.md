# TODO

## v1.x

- [x] Add example of input in csv file in README.md
- [x] Support load entities from csv
- [x] Customize prefix in seeder (default=`!`)
- [x] Customize prefix in validator (default=`!`)
- [x] relationship entity no longer required `model` key since the program will search it for you, but can also be
  overridden by providing a model data instead as it saves performance time
- [x] Add test case for overriding default reference prefix
- [ ] Update README description
- [x] Add docstrings
- [ ] Refactor test instances and test cases

## Tentative Plans

- Support load entities from excel
- any order of entities will not affect in seeding
  - approach: failed entity will be pushed back to the last to wait to be seed again
