# TODO

- [ ] Customize prefix in seeder (default=`!`)
- [x] Customize prefix in validator (default=`!`)
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
        - alternative, by getting the mappers, we can check its classes by searching
          in `list(models.Employee.registry.mappers)`, first, get the table name of the attribute with foreign
          key `str(list(Employee.company_id.foreign_keys)[0].column.table)`, then use it to iterate through the mappers by
          looking for its match table name `table_name == str(mapper.class_.__table__)`

- seed entities from csv file
    - limitations: does not support reference relationships
