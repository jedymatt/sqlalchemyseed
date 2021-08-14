# TODO

- [ ] Customize prefix in seeder (default= `!`)
- [x] Customize prefix in validator (default= `!`)
- [ ] relationship entity no longer need `model` key since the program will search it for you
- [x] HybridSeeder filter from foreign key id
- [x] HybridSeeder
- [x] Seeder
- [x] Validator
- [x] Added prefix '!' to relationship attributes

# In Progress

- Customize prefix
    - affected by changes: validator and seeder
    - solution to get model from a relationship attribute:
        - `models.Employee.company.mapper.class_`
- reference relationship attribute no longer need to add `model` key
    - affected by changes: validator and seeder

## Tentative Features

- reference foreign key attribute no longer need `model` key
    - affected by change: validator and seeder
    - searching for possible solution: get model from foreign key attribute

- seed entities from csv file
    - limitations: does not support reference relationships
