# Explicit scope boundary
This increment implements application-container CI/CD. Docker is not virtual hardware, and this package does not flash or boot QEMU.
Next: create a Yocto application recipe and image, choose a supported QEMU machine, configure SSH, and add host-to-target acceptance adapters.
Keep firmware/kernel/rootfs artifacts distinct from container images. The registry can store container artifacts; use a generic artifact repository for the first bootable image delivery.
pytest: Python test framework on the automation host.
Robot Framework: readable acceptance suites on the automation host.
Yocto ptest: package tests installed/executed on the target; add only once the Yocto layer exists.
Tests in this increment validate a local executable inside the builder image. Label them host integration/acceptance, not HiL.
Before deploying to real hardware add board compatibility, signing, recovery, power-control and hardware-specific test planning as required by the product.
