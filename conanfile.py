from conans import ConanFile, CMake, tools
import os.path


class OpenmeshConan(ConanFile):
    name = "OpenMesh"
    version = "7.1"
    license = "BSD-3-Clause"
    url = "https://github.com/yuweishan/conan-OpenMesh"
    description = "OpenMesh is a generic and efficient data structure for representing and manipulating polygonal meshes."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    scm = {
        "type": "git",
        "url": "https://www.graphics.rwth-aachen.de:9000/OpenMesh/OpenMesh.git",
        "revision": "OpenMesh-"+version,
        "subfolder": "OpenMesh",
    }

    def source(self):
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("OpenMesh/CMakeLists.txt", "    project (OpenMesh)", '''\
    project (OpenMesh)
    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup()''')

        # disable documentation build
        tools.replace_in_file("OpenMesh/CMakeLists.txt", "add_subdirectory (Doc)", "")

        # disable "d" suffix for Debug build
        tools.replace_in_file("OpenMesh/CMakeLists.txt", 'set (CMAKE_DEBUG_POSTFIX "d")', '')

        # do not build both shared and static library for non-Windows builds
        tools.replace_in_file("OpenMesh/src/OpenMesh/Tools/CMakeLists.txt", "target_link_libraries (OpenMeshToolsStatic OpenMeshCoreStatic)", "")
        tools.replace_in_file("OpenMesh/src/OpenMesh/Tools/CMakeLists.txt", "add_dependencies (fixbundle OpenMeshToolsStatic)", "")

    def build(self):
        # choose shared/static for Windows builds
        tools.replace_in_file("OpenMesh/CMakeLists.txt", "set( OPENMESH_BUILD_SHARED false", "set( OPENMESH_BUILD_SHARED " + ("true" if self.options.shared else "false"))

        # do not build both shared and static library for non-Windows builds
        tools.replace_in_file("OpenMesh/src/OpenMesh/Core/CMakeLists.txt", "SHAREDANDSTATIC", "SHARED" if self.options.shared else "STATIC")
        tools.replace_in_file("OpenMesh/src/OpenMesh/Tools/CMakeLists.txt", "SHAREDANDSTATIC", "SHARED" if self.options.shared else "STATIC")

        cmake = CMake(self)
        cmake.configure(defs={"BUILD_APPS": "OFF"}, source_folder="OpenMesh")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["OpenMeshCore", "OpenMeshTools"]
