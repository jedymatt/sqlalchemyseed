import unittest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from sqlalchemyseed.aio import AsyncHybridSeeder, AsyncSeeder
from tests.models import Base, Company, Employee


class AsyncSeederTestCase(unittest.IsolatedAsyncioTestCase):
    """Tests the async wrappers against an in-memory async SQLite engine."""

    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.session = AsyncSession(self.engine)

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def test_seed_nested_relationship(self):
        entities = {
            "model": "tests.models.Company",
            "data": {
                "name": "MyCompany",
                "!employees": [
                    {"data": {"name": "Alice"}},
                    {"data": {"name": "Bob"}},
                ],
            },
        }

        seeder = AsyncSeeder(self.session)
        await seeder.seed(entities)
        await self.session.commit()

        companies = (await self.session.execute(select(Company))).scalars().all()
        employees = (await self.session.execute(select(Employee))).scalars().all()
        self.assertEqual(len(companies), 1)
        self.assertEqual(companies[0].name, "MyCompany")
        self.assertEqual({e.name for e in employees}, {"Alice", "Bob"})
        self.assertEqual(len(seeder.instances), 1)

    async def test_seed_without_add_to_session(self):
        entities = {"model": "tests.models.Company", "data": {"name": "Ghost"}}

        seeder = AsyncSeeder(self.session)
        await seeder.seed(entities, add_to_session=False)
        await self.session.commit()

        companies = (await self.session.execute(select(Company))).scalars().all()
        self.assertEqual(companies, [])
        self.assertEqual(len(seeder.instances), 1)

    async def test_hybrid_seed_filter_references_existing_row(self):
        """The 'filter' key runs a query mid-seed, exercising real async
        driver I/O through run_sync."""
        await AsyncHybridSeeder(self.session).seed(
            {"model": "tests.models.Company", "data": {"name": "Acme"}}
        )
        await self.session.commit()

        hybrid = AsyncHybridSeeder(self.session)
        await hybrid.seed(
            {
                "model": "tests.models.Employee",
                "data": {
                    "name": "Carol",
                    "!company": {"filter": {"name": "Acme"}},
                },
            }
        )
        await self.session.commit()

        carol = (
            await self.session.execute(
                select(Employee).where(Employee.name == "Carol")
            )
        ).scalar_one()
        acme = (
            await self.session.execute(
                select(Company).where(Company.name == "Acme")
            )
        ).scalar_one()
        self.assertEqual(carol.company_id, acme.id)

    async def test_async_strict_raises_on_scalar_list(self):
        import sqlalchemyseed.errors as errors
        entities = {
            "model": "tests.models.Employee",
            "data": {
                "name": "Bob",
                "!company": [
                    {"model": "tests.models.Company", "data": {"name": "C0"}},
                    {"model": "tests.models.Company", "data": {"name": "C1"}},
                ],
            },
        }
        seeder = AsyncSeeder(self.session, strict=True)
        with self.assertRaises(errors.InvalidTypeError):
            await seeder.seed(entities)

    async def test_async_hybrid_strict_raises_on_scalar_list(self):
        import sqlalchemyseed.errors as errors
        entities = {
            "model": "tests.models.Employee",
            "data": {
                "name": "Bob",
                "!company": [
                    {"model": "tests.models.Company", "data": {"name": "C0"}},
                    {"model": "tests.models.Company", "data": {"name": "C1"}},
                ],
            },
        }
        seeder = AsyncHybridSeeder(self.session, strict=True)
        with self.assertRaises(errors.InvalidTypeError):
            await seeder.seed(entities)


if __name__ == "__main__":
    unittest.main()
