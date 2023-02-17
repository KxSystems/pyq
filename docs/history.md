---
title: PyQ version history – Interfaces – kdb+ and q documentation
description: Version history of the PyQ interface between kdb+ and Python
author: Alex Belopolsky, Aleks Bunin
keywords: history, interface, kdb+, library, pyq, python, q, version
---
# ![PyQ](../img/pyq.png) Version history



## Version 4.2.1

Released on 2019-02-12

- Fixed a bug preventing installation from source tarball.
- Updated classifiers and supported operating systems.

## Version 4.2.0

Released on 2019-02-11

Deprecations and removals:

- !631 - #993 Delete documentation -- PyQ's documentation available at [code.kx.com](../../interfaces/pyq/index.md).
- !672 - #1017 Deprecate py2 - Python 2.7 support will end in December 2019. Future versions of PyQ will not support Python 2.7. PyQ 4.2.x will be latest series to support Python 2.7 and will receive bug-fixes until end of December 2019.

Enhancements:

- !609 - #979 Implemented K.dict and K.table constructors.
- !618, !647, !679 - #985 Integration of embedPy [gh-30](https://github.com/KxSystems/pyq/issues/30)
- !642 - #650 Convert objects supporting new buffer protocol to K
- !644 - #1007 Implemented K._knt to call the new knt(J,K) function from k.h.
- !648 - #784 Pass command line arguments after -- directly to q.
- !650 - #784 More command-line arguments to be recognized by pyq executable
- !671 - #1030 Support Python 3.7 [gh-80](https://github.com/KxSystems/pyq/issues/80)

Bug fixes:

- !660 - #1013 K._F accelerator should accept None entries
- !661, !678 - #1015, #1035 Fixed LGTM alerts
- !662 - #1021 Use correct ANSI C header errno.h
- !667 - #1023 cherry-pick GH PRs
- !668 - #1025 K(None).null must be 1b
- !669 - #1027: Simplify executable path lookup on Linux
- !673 - #986 Use sysconfig instead distutils.sysconfig in setup.py
- !674 - #877 Remove GC support for K iterators
- !675 - #1034 Fixed numpy warnings in tests
- !676 - #1024 Check that python lib exists
- !677 - #826 Block .data on t=0 k lists
- !680 - #1028 Fixed clang warnings.
- !682 - #1036 Convert 0N to NaT.

Tests and CI:

- !635 - #985 Use taskset in the run_q.sh script.
- !664 - #1022 Run pyq executable tests under valgrind

## Version 4.1.4


Released on 2018-06-18

Bug fixes and enhancements

- !629 - BUG #992 Fixed conversion of mixed lists with Unicode entries to q.
- !630 - ENH #994 Allow None and Python 2.x Unicode in `K._S` accelerator.
- !633 - ENH #995 Optimize conversion for masked array.
- !634 - BUG #996 Fixed getitem for kdb+ V3.6.
- !636 - MNT #000 Fix codestyle failures.
- !640 - BUG #1003 Fixed `getitem` in the case of legacy 32-bit enums.
- !641 - BUG #1005 Fix translation of Windows paths to k
- !643 - ENH #0000 Updated `k.h` to the latest version 2018.05.24.
- !646 - BUG #957 Improve detection of standalone Python
- !651 - BUG #1008 Added logic to find Python DLL from sysconfig.
- !653 - ENH #703 Create conda package

CI

- !632 - TST Use numpy 1.14; drop numpy 1.12 in tests.
- !654 - TST #1010 Skip infinite recursion tests when measuring coverage
- !655 - BUG #997 Fixed wrongdoings in CI


Documentation

This is the last release series, where documentation is included with the PyQ source. Starting with PyQ 4.2.0 documentation will be available only at [code.kx.com](../../interfaces/pyq/index.md).


## Version 4.1.3

Released on 2018-03-06

Bug fixes and enhancements

- !604 - BUG #970 Ignore the first line in the `otool -L` output.
- !608 - ENH #980 Implemented `K.guid.na`.
- !610 - STY #916 C code reformat
- !614 - ENH #919 Rewrote `z2py` entirely in C.
- !616 - MNT #984 Speed up access to q built-ins.
- !617 - ENH #936 Support for kdb+ V3.6
- !622 - BUG #988 Use `/sbin/ldconfig` if `ldconfig` not in the `PATH`.
- gh-33 - MNT Define `_GNU_SOURCE` conditionally.
- gh-38 - MNT Update `k.h`.


Documentation

This is the last release, where documentation included with the PyQ source. Starting with PyQ 4.2.0, documentation will be available only at [code.kx.com](../../interfaces/pyq/index.md).

- !621 - MNT Update metadata and authors list
- gh-26 - MNT Updated the license entry in the package classifiers.

CI

- gh-27, gh-29, gh-46 - BLD Travis CI configuration.
- gh-39 - BLD Denylist pytest 3.3.0.
- gh-45 - BLD Send coverage results to Codecov

## [Version 4.1.2](https://pyq.readthedocs.io/en/pyq-4.1.2/)

Released 2017.10.12

Bug fixes and enhancements

- !589 – BUG #955 Check for negative values (including `0Ni`) in enums.
- !590 – BUG #956 Do not use `clr`.
- !591 – ENH #958 Support for building wheels.
- !594 – BUG #960 Do not colorize the `q)` prompt on Windows.
- !597 – BUG #962 Removed 'collections' from `lazy_converters`.
- !598 – MNT #963 Fixed issue identified by lgtm.com.

Documentation

- !588 – DOC #954 Windows documentation.
- !595 – DOC #961 Fixed a typo in an introductory example.
- !599 – DOC #964 Updated documentation in preparation for 4.1.2 release.


## [Version 4.1.1](https://pyq.readthedocs.io/en/pyq-4.1.1/)

Released 2017.09.21

Bug fixes and enhancements

- !579 – BUG #948 Fixed compile errors on Windows with kdb+ &lt; V3.5.
- !577 – BUG #946 Fixed compilation errors for Python 2.7 on Windows.
- !582 – ENH #950 Explain how to properly start PyQ when launching from stock Python.

Documentation

- !583 – DOC #951 Updated links to the new kx.com website.

CI

- !584 – TST #952 Attempt to fix failing tests on Windows.


## [Version 4.1.0](https://pyq.readthedocs.io/en/pyq-4.1.0/)

Released 2017.08.30

New features

- !519 – #889: Multi-threading support.
- !542 – #917: traceback support.
- Experimental Windows support
  - !507 – #900: Windows support.
  - !508 – #900: Windows support py36.
  - !527 – #900: Fixed a few tests that failed under Windows.
  - !562 – BLD #934 windows ci.
  - !564 – TST #900 Fix/skip tests that fail on Windows.

Enhancements

- !503, !568 – #659: New setup.py
- !560 – ENH #933 Use dot(K, K) for kdb+ versions &gt;= 3.5
- !558 – #880 Fix ktd bug
- !552 – TST #920 Test `±0Wt` conversions to Python.
- !550 – ENH #925 Define `Q_VERSION` and similar constants in `_k.c`.
- !549 – ENH #925: Define QVER once, use everywhere.
- !548 – ENH #924 Allow returning arbitrary objects from python calls.
- !545 – ENH #921 Handle passing keyword arguments to functions in C.
- !544 – #919: Remove x2l objects
- !520 – #615: BUG: Empty symbol list converts to float array.

KX

- !539, !569 – Updated k.h.
- !566 – #937 Add Apache 2.0 license for kx owned components.

Documentation

- !510 – Use locally stored intersphinx inventory.
- !515 – #895: PyQ 4.0 presentation
- !532 – #914: Use new kx.code.com
- !553 – DOC #805 Updated the description in the README file.
- !554 – DOC #805 Added links to long description.
- !557 – DOC #929 Add macOS installation instructions
- !572 – DOC #890 What's new in 4.1.

CI

- !513 – #904 Add Centos 7 x64 docker image to CI runs
- !559 – BLD #935 Change default kdb+ version to 3.5.
- !561 – TST #930 Test 64-bit installation on macOS.
- !565 – BLD #938 Denylist pytest 3.2.0, due to a bug.
- !570 – BLD Closes #940 Test using Python 2.7, 3.5 and 3.6; numpy 1.12 and 1.13.
- !571 – BLD #867 Add setup option when we remove setuptools.
- !531 – #909 Added ubuntu job to CI in develop branch


## [Version 4.0.3](https://pyq.readthedocs.io/en/pyq-4.0.3/)

Released 2017.07.17

Bug fixes:

- !551 – BUG #922: Allow large (`>2**31`) integers in `K._ktn()`.
- !546 – BUG #923 Fixed conversion of mixed lists.

Documentation:

- !547 – DOC: Minor documentation corrections

## [Version 4.0.2](https://pyq.readthedocs.io/en/pyq-4.0.2/)

Released 2017.05.12

Enhancements:

- !523 – #909: Support installing PyQ on Ubuntu 16.04.
- !528 – #911: qp and pq: set console size in q when running ptpython scripts.
- !535 – #910: qp: exit from q) prompt on Ctrl-D.
- !536 – #912: qp: report error and exit if pre-loading fails.

Documentation:

- !537 – #909: Added a guide on installing PyQ on Ubuntu.
- !533 – #914: Use new kx.code.com.

## [Version 4.0.1](https://pyq.readthedocs.io/en/pyq-4.0.1/)

Released 2017.03.15

Enhancements:

- !509 – #903: Fixed a reference leak in debug build and a gcc 4.8.5 compiler warning.
- !505 – #901: Provide a fallback for systems that lack CPU\_COUNT, e.g. RHEL 5.
- !502 – #899: Corrected integer types on 32-bit systems and added explicit casts when necessary.

Documentation:

- !511 – Use locally stored intersphinx inventory.
- !506 – #902 Updated README.

## [Version 4.0](https://pyq.readthedocs.io/en/pyq-4.0/)

Released 2017.03.02

New Features:

- !365 – #756: Expose okx from k.h in Python.
- !376 – #806: Hooked basic prompt toolkit functionality into cmdtloop.
- !384 – #809: Implemented the qp script - like pq but start at the q) prompt.
- !385 – #806: Add bottom toolbar to q) prompt.
- !378 – #809: Implemented ipyq and pq scripts.
- !387 – #813: Implemented the @ operator.
- !401 – #828: Implemented type-0 list to array conversions.
- !402 – #775: Implemented getitem for enumerated lists.
- !404 – #833: Implemented `K.___sizeof__()` method.
- !359 – #642: Implement typed constructors and casts
- !390 – #815: Implemented the data attribute for the K objects in C.
- !396 – #829: Implemented basic nd &gt; 1 case: C contiguous and simple type.
- !410 – #840: Implemented shift operators.
- !420 – #851: Implemented setm() and m9() in `_k`.
- !422 – #852: Implemented conversion from arbitrary sequences to K.
- !428 – #835: Implemented `K.__rmatmul__`.
- !432 – #856: Implemented file system path protocol for file handles.
- !435 – #598: Added support for pathlib2.
- !437 – #855: Added support for complex numbers.
- !439 – #791: Implemented `_n` attribute for K objects.
- !467 – #873: Implement K.timespan(int) constructor

Enhancements:

- !297 – #752: More datetime64 to q conversions
- !314 – #672: Improve calling Python functions from q
- !315 – #766: Defined the `__dir__` method for class `_Q`.
- !316 – #767: Make "exec" method callable without trailing `_` in PY3K
- !330 – #779: Reimplemented new and call in C
- !352 – #792: Restore support for KXVER=2.
- !354 – #796: Conversion of "small" kdb+ longs will now produce Python ints under Python 2.x.
- !355 – #769: Restore array struct
- !358 – #798: Revisit array to k conversions.
- !375 – #791: K object attributes
- !377 – #807: Clean up and reuse the list of q functions between K and q
- !379 – #808: Clean up pyq namespace
- !380 – #791: Replaced .inspect(b't') with `._t`.
- !381 – #806: Return to Python prompt when Control-D or Control-C is pressed.
- !382 – #659: Get rid of KXVER in the C module name.
- !383 – #810: Clean up q namespace
- !388 – #779, #798: Removed unused variables.
- !389 – #818: Use fully qualified name for the internal K base class.
- !391 – #816: temporal data lists to array conversion
- !394 – #823: Preload kdb+ database if provided on pyq command line.
- !397 – #830: Make sure strings obtained from q symbols are interned.
- !398 – #806: Added a simple word completer.
- !399 – #819: Make K.string accept Unicode in Python 2.x and bytes in Python 3.x.
- !400 – #806: Clean python exit on `\\`
- !405 – #836: Reimplemented `K.__bool__` in C.
- !406 – #837: Reimplemented `K.__get__` in C.
- !408 – #838: Install sphinxcontrib-spelling package in the deploy stage.
- !413 – #842: K to bytes conversion
- !423 – #852: Added special treatment of symbols in `_from_sequence()`; allow mixed lists in conversions.
- !424 – #852: Fixed the case of empty sequence. Use `K._from_sequence` as a tuple converter.
- !425 – #852: Remove dict workaround
- !426 – #853: Make `dict[i]` consistent with `list[i]`
- !429 – #854: Walk up the mro to discover converters
- !430 – #608: Return K from mixed K - numpy array operations.
- !431 – #679: Fixed conversion of enumeration scalars into strings.
- !442 – #808: pyq globals clean-up
- !443 – #858: The "nil" object does not crash show() anymore.
- !444 – #817: Clip int(q('0N')) to -0W when building K.long lists.
- !445 – #857: Adverbs revisited
- !446 – #861: Allow unary and binary ops and projections to be called with keywords.
- !447 – #857: Use vs (sv) instead of `each_left` (`right`).
- !449 – #864: Corrected the date bounds and added a comprehensive test.
- !450 – #865: Fixed x.char cast
- !455 – #863: Allow out-of-range scalar dates to be converted to ±0Wd.
- !460 – #870: K.timestamp bug
- !470 – #874: K.boolean redesign
- !477 – #875: Make sure bool(enum scalar) works in various exotic scenarios.
- !481 – #881: `K._ja` bug
- !483 – #850: Use py2x converters in atom constructors.
- !485 – #882: Return 0w on overflow
- !486 – #883: Make boolean constructor stricter : Allow only integer-like values in `K._kb()`.
- !487 – #884: Detect mappings in typed constructors.
- !490 – #841: Fixed `mv_release`.
- !492 – #886: Fix two bugs in pyq executable; improve setup tests
- !494 – #891: Fix crash in `K._kc()`

CI and tests improvements:

- !349, !456, !456, !471, !457, !459, !464 – #695, #793, #867: Improvements in code coverage reporting.
- !350 – #794: Run pycodestyle in tox.
- !411 – #827: Use Python 3.6 and 2.7.13 in CI.
- !415, !451 – #845: Use Docker for CI
- !433 – #679: Fixed test on kdb+ 2.x.
- !436 – Add numpy 1.12 to the CI tests.
- !440 – #803: keywords and descriptions from code.kx.com.
- !452 – Add kdb+ 3.5t to the CI tests.
- !461 – #866: Added tests and fixed timestamp range.
- !475 – Use random CPU and limit one CPU core per job in CI.
- !489 – #885: Reformatted code in test files.
- !318, !351, !474, !478, !479, !480, !484, !488, !491 – #768: Improve C code test coverage.

Documentation:

- !341 – #789: Updated README: Test section.
- !353 – #764: simpler docstrings
- !360 – #764: Reorganized documentation. Minor fixes.
- !361 – #764: More docs improvements
- !362 – #764: docs improvements
- !366 – #764: test docs build in tox
- !371 – #803: Updated 32-bit Python/PyQ guide to use Python 3.6.
- !374 – #804: doc style improvements
- !373 – #764 and #777 table to array and sphinx doctest
- !392 – #820: What's New in 4.0
- !403 – #832: spellcheck docs
- !407 – #838: Add doc path to sys.path in conf.py.
- !409 – #803 Docs additions
- !412 – #803: Make documentation testing a separate stage.
- !427 – #803: more docs
- !448 – #803: More docs
- !469 – #871: More docs
- !438 – #854 (#820): Added a what's new entry about named tuples conversion.
- !472 – #803: Added adverbs documentation
- !493 – #803: Document calling Python from q
- !462, !463, !465, !468, !473 – Logo improvements

Setup:

- !337 – #782: Use install extras to install requirements.
- !339 – #782: Use extras instead of deps in tox.ini.
- !340 – #788: Add ipython extras.

<!-- ## [Version 3.8.5](https://pyq.readthedocs.io/en/pyq-3.8.5/) 404 RESPONSE 2019.09.02 -->
## Version 3.8.5

Released 2017.03.16

- !517 – #901: Provide a fallback for systems that lack `CPU_COUNT`.

## [Version 3.8.4](https://pyq.readthedocs.io/en/pyq-3.8.4/)

Released 2017.01.13

- !414 – #843: Setup should not fail if `VIRTUAL_ENV` is undefined
- !395 – #825: Fixed uninitialized "readonly" field in getbuffer

## [Version 3.8.3](https://pyq.readthedocs.io/en/pyq-3.8.3/)

Released 2016.12.15

- !357 – #799: Several documentation fixes.
- !368 – #802: Setup should not fail if `$VIRTUAL_ENV/q` does not exist.

## [Version 3.8.2](https://pyq.readthedocs.io/en/pyq-3.8.2/)

Released 2016.12.01

Documentation improvements:

- !306 – #763: Update README.md - fixed INSTALL link.
- !312 – Fix formatting; ?? -&gt; date of the release in the CHANGELOG.
- !322 – Fixed formatting error in the documentation.
- !324 – #744: use pip to install from the source.
- !338 – #785: Virtual environment setup guide.
- !346 – #764: docs improvements
- !342 – #787: Added links to rtd documentation.

PyQ executable improvements:

- !310 – #761: Allow PyQ executable to be compiled as 32-bit on 64-bit platform.
- !329 – #646: Print PyQ, KDB+ and Python versions if --versions option is given to pyq.
- !332 – #646: Print full PyQ version.
- !333 – #781: Find QHOME when q is installed next to bin/pyq but no venv is set.
- !336 – #783: Fixed a bug in CPUS processing
- !345 – #646: Added NumPy version to --versions output.

Other improvements and bug fixes:

- !308 – #759: Return an empty slice when (stop - start) // stride &lt; 0.
- !320 – #771: Workaround for OrderedDict bug in Python 3.5
- !323 – #773: Renamed ipython into jupyter; added starting notebook command.
- !326 – #720: Simplified the test demonstrating the difference in Python 2 and 3 behaviors.
- !327 – #720: Finalize embedded Python interpreter on exit from q.
- !331, !343 – #768: Improve C coverage

Improvement in the (internal) CI:

- !305, !309, !311, !321, !335, !347 – Multiple improvements in the CI.
- !319 – #770: Run doctests in tox.

## [Version 3.8.1](https://pyq.readthedocs.io/en/pyq-3.8.1/)

Released 2016.06.21

- !292 – #744: Print guessed path of q executable when exec fails.
- !293, !294 – #748 Use `VIRTUAL_ENV` environment variable to guess QHOME.
- !301, !295 – #751: Update documentation.
- !296 – #750: Fall back on 32-bit version of q if 64-bit version does not run.
- !298, !299, !300, !303 – #753: CI Improvements.
- !302 – #755: Use preserveEnumerations=1 option to b9 instead of -1.

## [Version 3.8](https://pyq.readthedocs.io/en/pyq-3.8/)

Released 2016.04.26.

- !256 – #670: Enable 32-bit CI
- !258 – #717 Expose sd0 and sd1 in python.
- !259 – #718 Added a test running "q test.p".
- !261 – Use Python 3.4.3 in CI
- !272, !273 – #731 Added Python 3.5.0 test environment and other CI improvements.
- !263 – #718 More p) tests
- !264 – #709 Redirect stderr and stdout to notebook
- !271 – #729 Conversion of lists of long integers to q.
- !274 – #728 Don't corrupt existing QHOME while running tox.
- !275 – #733 Don't add second soabi for Python 3.5.
- !276 – #734: Added support for enums in memoryview.
- !277 – #736: Implemented format() for more scalar types.
- !278 – #737 Misleading error message from the list of floats conversion.
- !279, !280 – #738 CI improvements
- !281 – #611: Updated k.h as of 2016.02.18
- !286, !288, !289, !290 – #742 PyQ Documentation
- !287 – #745: Automatically generate version.py for PyQ during setup.

## Version 3.7.2

Released 2015.07.28.

- !270 – #726 Reuse dict converter for OrderedDict.
- !267 – #724 and #723 numpy &lt;&gt; q conversion fixes.
- !266 – #725 Use 001..002 to bracket ANSI escapes.
- !265 – #721 Made slicing work properly with associations (dictionaries) and keyed tables.
- !260 – #719 Backport python 3 bug fixes.
- CI Improvements (!257, !262, !269, !268).

## Version 3.7.1

Released 2015.02.12.

- !244 – #701 Fixed using q datetime (z) objects in format().
- !246 – Removed pytest-pyq code. pytest-pyq is now separate package.
- !247 – #709 IPython q-magic improvements
- !248 – #673 Implemented Unicode to q symbol conversion in python 2.x.
- !249, !252 – #691 Improved test coverage
- !250, !251 – #695 Use Tox as test-runner
- !253 – #715 Fixed table size computation in getitem.
- !255 – #691 Remove redundant code in slice implementation

## Version 3.7

Released 2015.01.15.

- !222 – #581 Implements conversion of record arrays.
- !223 – #680 Fixed int32 conversion bug.
- !224 – #681 Fixed datetime bug - freed memory access.
- !225 – Added support for numpy.int8 conversion.
- !226 – #644 Fixed descriptor protocol.
- !227 – #663 Fixed nil repr (again).
- !228, !233, !237, !239 – #687 Updates to documentation in preparation to public release.
- !229 – #690 Use only major kx version in `_k` module name.
- !230 – #691 Added tests, fixed date/time list conversion.
- !232 – #693 Implement pyq.magic.
- !234 – #694 Use single source for python 2 and 3. (No 2to3.)
- !235 – #674 Added support for nested lists.
- !236 – #678 Fixed compiler warnings.
- !238 – #657 Make numpy optional.
- !240 – #674 Added support for nested tuples.
- !241 – #696 Implemented slicing of K objects.
- !242 – #699 int and float of non-scalar will raise TypeError.
- !243 – #697 Fixed a datetime bug.

## Version 3.6.2

Released 2014.12.23.

- !198 – #654 Restore python 3 compatibility
- !211 – #667 Added pyq.c into MANIFEST
- !213 – #669 Fixed a crash on Mac
- !214 – #590 Implemented numpy date (M8) to q conversion
- !215, !216 – #590 Implemented support for Y, M, W, and D date units
- !217, !218, !220, !221 – #666 Multiple CI improvements
- !219 – #676 Implemented numpy.timedelta64 to q conversion

## Version 3.6.1

Released 2014.11.06.

- !206 – #663 Fixed nil repr
- !207 – CI should use cached version of packages
- !208 – #665 Allow K objects to be written into ipython zmq.iostream
- !209 – Show python code coverage in CI
- !210 – #666: Extract C and Python coverage to print in the bottom of the CI run
- !212 – Bump version to 3.6.1b1

## Version 3.6.0

Released 2014.10.23.

- !189 – #647 Fix pyq.q() prompt
- !190 – CI should use Python 2.7.8
- !191 – #648 Boolean from empty symbol should be False
- !192 – #634: Moved time converter to C and removed unused converters
- !193 – #652 Added `__long__` method to K type.
- !194 – #653 Allow K integer scalars to be used as indices
- !195, !197 – #651 Format for scalar types D, M, T, U, and V.
- !196 – #611 Updated k.h to 2014.09.11
- !199 – #656 Iteration over K scalars will now raise TypeError.
- !200 – #655 Added support for Python 3 in CI
- !202 – #571 Added support for uninstalling Q components
- !203 – #633 Improve test coverage
- !204 – #633 Added boundary and None checks in ja

## Version 3.5.2

Released 2014.07.03.

- !184, !186 – #639 taskset support. Use CPUS variable to assign CPU affinity.
- !187 – #641 color prompt
- !185 – #640 Restore minimal support for old buffer protocol

## Version 3.5.1

Released 2014.06.27.

- !177, !178 – #631 pyq is binary executable, not script and can be used in hashbang.
- !179 – #633 Added memoryview tests.
- !181 – #636 Moved extension module into pyq package.
- !182 – #633 Removed old buffer protocol support.
- !183 – #638 Calling q() with no arguments produces an emulation of q) prompt

## Version 3.5.0

Released 2014.06.20.

- !164 – #611 Updated k.h
- !165 – #614 Expose jv
- !166 – #580 Show with output=str will return string
- !167 – #627 Fixed p language
- !168 – Fix for pip, PyCharm and OS X
- !169 – #629 python.py script was renamed to pyq
- !170 – #632 jv reference leak
- !171 – #633 C code review
- !172 – #634 k new
- !173 – #612 Generate C code coverage for CI
- !174, !175 – #633 test coverage
- !176 – #635 Disable strict aliasing

## Version 3.4.5

Released 2014.05.27.

- 614: Expose dj and ktj
- 620: Empty table should be falsy
- 622: Convert datetime to "p", not "z"

## Version 3.4.4

Released 2014.05.23.

- python.q returns correct exit code

## Version 3.4.3

Released 2014.04.11.

- 617: Dict Conversion
- 619: Len Keyed Table

## Version 3.4.2

Released 2014.04.11.

- 589: Symbol array roundtripping
- 592: Properly register py.path.local
- 594: Support passing additional values to select/update/exec methods.
- 595: Implement `pytest_pyq` plugin
- 596: Implement python dict converter
- 601: Add support for ^ (fill) operator
- 602: Fix r-ops for non-commutative operations.
- 603: Fix unary + and implement unary ~
- 604: Make all q methods accessible from pyq as attributes
- 609: Updated k.h to the latest kx version
- NUC: Only true division is supported. Use "from \_\_future\_\_ import division" in python 2.x.

## Version 3.4.1

Released 2014.03.14.

- Add support for char arrays #588
- PyQ can now be properly installed with pip -r requirements.txt #572

## Version 3.4

Released 2014.03.07.

- Issues fixed: #582, #583, #584, #586
- Support dictionary/namespace access by .key
- Support ma.array(x) explicit conversion
- Add support for comparison of q scalars

## Version 3.3

Released 2014.02.05.

- Issues fixed: #574, #575, #576, #577, #578

## Version 3.2

Released 2013.12.24.

- Issues fixed: #556, #559, #560, #561, #562, #564, #565, #566, #569, #570, #573
- NEW: wrapper for python.q to use it under PyCharm
    Note: You will need to create symlink from python to python.py in order for this to work, i.e.: ln -s bin/python.py bin/python

- Support to use 32-bit Q under 64-bit OS X

## Version 3.2.0 beta

- Convert int to KI if KXVER &lt; 3, KJ otherwise
- In Python 2.x convert long to KJ for any KXVER

## Version 3.1.0

Released 2012.08.25.

- support Python 3.2
- release pyq-3.1.0 as a source archive

## 2012.08.10

- basic guid support

## Version 3.0.1

Released 2012.08.09.

- support both q 2.x and 3.x
- better setup.py
- release pyq-3.0.1 as a source archive

## 2009.10.23

- NUC: k3i
- K(None) =&gt; k("::")
- K(timedelta) =&gt; timespan

## 2009.01.02

- Use k(0, ..) instead of dot() and aN() to improve compatibility
- Default to python 2.6
- Improvements to q script.p
- NUC: extra info on q errors

## 2007.03.30

- implemented `K._ja`

## Version 0.3

- Added support for arrays of strings

## Version 0.2

- Implemented iterator protocol.
