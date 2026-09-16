CXX = clang++
CXXFLAGS = -std=c++17 -O3 -DNDEBUG -Wall -Wextra -Wpedantic
JAVAC = javac
JAVA = java
JAVAFLAGS = --release 17 -d build
JAVA_SOURCES = src/Sorting.java src/MersenneTwister.java src/Benchmark.java src/Demo.java src/Tests.java
JAVA_MARKER = build/.java-classes

.PHONY: all test sanitize java-all java-test cpp-all cpp-test cpp-sanitize clean
all: java-all

java-all: $(JAVA_MARKER)

$(JAVA_MARKER): $(JAVA_SOURCES) | build
	$(JAVAC) $(JAVAFLAGS) $(JAVA_SOURCES)
	touch $@

java-test: java-all
	$(JAVA) -cp build Tests

test: java-test

# Java does not have an AddressSanitizer equivalent in this project; run the
# complete Java correctness suite for the default sanitizer target.
sanitize: java-test

# The original C++ implementation is retained as an optional reference build.
cpp-all: build/benchmark-cpp build/demo-cpp

build/benchmark-cpp: src/benchmark.cpp src/sorting.hpp | build
	$(CXX) $(CXXFLAGS) src/benchmark.cpp -o $@

build/demo-cpp: src/demo.cpp src/sorting.hpp | build
	$(CXX) $(CXXFLAGS) src/demo.cpp -o $@

build:
	mkdir -p build

cpp-test: build/tests-cpp
	./build/tests-cpp

build/tests-cpp: src/tests.cpp src/sorting.hpp | build
	$(CXX) $(CXXFLAGS) src/tests.cpp -o $@

cpp-sanitize: | build
	$(CXX) -std=c++17 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -Wall -Wextra src/tests.cpp -o build/tests-sanitize
	./build/tests-sanitize

clean:
	rm -f build/benchmark build/demo build/tests build/tests-sanitize
	rm -f build/benchmark-cpp build/demo-cpp build/tests-cpp build/tests-sanitize
	rm -f $(JAVA_MARKER) build/*.class
