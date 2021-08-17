# TODO

## v1.0.0

- [ ] Add example of input in csv file in README.md
- [x] Support load entities from csv
- [ ] Customize prefix in seeder (default=`!`)
- [x] Customize prefix in validator (default=`!`)
- [ ] relationship entity no longer required `model` key since the program will search it for you, but can also be
  overridden by providing a model data instead as it saves time

# In Progress

- Customize prefix
    - affected by changes: validator and seeder

- reference relationship attribute no longer need to add `model` key
    - affected by changes: validator and seeder
    - solution to get model class from a relationship attribute example:
        - `models.Employee.company.mapper.class_`
- reference foreign key attribute no longer need `model` key
    - affected by change: validator and seeder
    - searching for possible solution by get model from foreign key attribute:
        - by getting the mappers, we can check its classes by searching in `list(models.Employee.registry.mappers)`,
          first, get the table name of the attribute with foreign
          key `str(list(Employee.company_id.foreign_keys)[0].column.table.name)`, then use it to iterate through the
          mappers by looking for its match table name `table_name == str(mapper.class_.__tablename__)`

## Tentative Features

- load entities from excel support
        