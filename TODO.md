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

- reference relationship attribute no longer need to add `model` key
    - affected by changes: validator and seeder
    - solution to get model class from a relationship attribute example:
        - `models.Employee.company.mapper.class_`

## Tentative Features

- reference foreign key attribute no longer need `model` key
    - affected by change: validator and seeder
    - searching for possible solution by get model from foreign key attribute:
        - none found yet
        - alternative, by getting the mappers, we can check its tablename and get its
          class, `list(models.Employee.registry.mappers)`, but we have to get the table name first to locate the
          referenced class in the mappers and get the model class

- seed entities from csv file
    - limitations: does not support reference relationships
