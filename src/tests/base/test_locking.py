import time

import pytest
from django.utils.timezone import now

from pretix.base.models import Event, EventLock, Organizer
from pretix.base.services import locking


@pytest.fixture
def event():
    o = Organizer.objects.create(name='Dummy', slug='dummy')
    event = Event.objects.create(
        organizer=o, name='Dummy', slug='dummy',
        date_from=now()
    )
    return event


@pytest.mark.django_db
def test_locking_exclusive(event):
    with event.lock():
        with pytest.raises(EventLock.LockTimeoutException):
            ev = Event.objects.get(id=event.id)
            with ev.lock():
                pass


@pytest.mark.django_db
def test_locking_different_events(event):
    other = Event.objects.create(
        organizer=event.organizer, name='Dummy', slug='dummy2',
        date_from=now()
    )
    with event.lock():
        with other.lock():
            pass


@pytest.mark.django_db
def test_lock_timeout_steal(event):
    locking.LOCK_TIMEOUT = 5
    locking.lock_event(event)
    with pytest.raises(EventLock.LockTimeoutException):
        ev = Event.objects.get(id=event.id)
        locking.lock_event(ev)
    time.sleep(6)
    locking.lock_event(ev)
    with pytest.raises(EventLock.LockReleaseException):
        locking.release_event(event)
