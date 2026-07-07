"""
Async wrappers around the synchronous seeders.

These bridge the existing sync-only seeder logic onto an ``AsyncSession``
using :meth:`~sqlalchemy.ext.asyncio.AsyncSession.run_sync`, which runs the
sync code inside a greenlet where the driver's blocking I/O is translated
into ``await`` calls.
No parallel async reimplementation of the traversal is needed.
"""

from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from .seeder import HybridSeeder, Seeder


class AsyncSeeder:
    """Async counterpart of :class:`~sqlalchemyseed.seeder.Seeder`."""

    def __init__(self, session: AsyncSession, ref_prefix: str = "!"):
        self.session = session
        self.ref_prefix = ref_prefix
        self._seeder: Seeder = None

    async def seed(self, entities: Union[list, dict], add_to_session: bool = True):
        def _run(sync_session):
            seeder = Seeder(sync_session, ref_prefix=self.ref_prefix)
            seeder.seed(entities, add_to_session=add_to_session)
            return seeder

        self._seeder = await self.session.run_sync(_run)

    @property
    def instances(self) -> tuple:
        return self._seeder.instances if self._seeder is not None else ()


class AsyncHybridSeeder:
    """Async counterpart of :class:`~sqlalchemyseed.seeder.HybridSeeder`.

    The hybrid seeder issues queries (``filter`` keys) *during* the seed
    traversal, so it genuinely needs a live connection; ``run_sync`` supplies
    a real sync ``Session`` whose queries are proxied to the async driver.
    """

    def __init__(self, session: AsyncSession, ref_prefix: str = "!"):
        self.session = session
        self.ref_prefix = ref_prefix
        self._seeder: HybridSeeder = None

    async def seed(self, entities: Union[list, dict]):
        def _run(sync_session):
            seeder = HybridSeeder(sync_session, ref_prefix=self.ref_prefix)
            seeder.seed(entities)
            return seeder

        self._seeder = await self.session.run_sync(_run)

    @property
    def instances(self) -> tuple:
        return self._seeder.instances if self._seeder is not None else ()
