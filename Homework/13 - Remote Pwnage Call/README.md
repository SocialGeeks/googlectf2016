Subcategory: Exploitation

It's astounding!

Time is fleeting

Madness takes it's toll...

Let's do the time warp again!

The service on ssl-added-and-removed-here.ctfcompetition.com:1831 is using the
following RPC specification file. Don't forget to account for SSL offloading
when completing this level.

struct d { int idx; opaque data; };

struct e { int idx; int size; };

/* bringing your RPC into the SUN / program TOKENPROG { version TOKENVERS { int
ALLOCATE(int sz) = 2; / allocate sz bytes of memory, return the index into the
list / void FREE(int idx) = 3; / free list[idx] if not null / void COPY(struct
d) = 5; / copy bytes into list[idx] / struct d INFOLEAK(struct e) = 7; / cause
an info leak? :P */ } = 1; } = 0x20001337;

The flag can be found in /app/flag


remote-pwnage-call.tar.xz
