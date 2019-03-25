from conans import ConanFile, CMake, tools

class OpenMeshConan(ConanFile):
    name = 'OpenMesh'
    version = '8.0'
    license = 'BSD-3-Clause'
    url = 'https://www.graphics.rwth-aachen.de:9000/OpenMesh/OpenMesh.git'
    description = 'OpenMesh is a generic and efficient library that offers data structures for repr esenting and manipulating polygonal meshes. It is a powerful tool for handling polygonal meshes. Due to its inherent generative structure it allows the user to create mesh types which are custom tailored to the specific needs of the application. The user can either supply his own data structures for representing vertices, edges and faces or he can conveniently use the predefined structures of OpenMesh. Additionally OpenMesh offers dynamic properties allowing the user to attach and detach data to the mesh during runtime.'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    default_options = 'shared=True'
    generators = 'cmake'
    scm = {
        'type': 'git',
        'url': 'https://www.graphics.rwth-aachen.de:9000/OpenMesh/OpenMesh.git',
        'revision': '37be8f8b0522fb121332ddffee3e6da6acdd8f7b',
        'subfolder': 'OpenMesh',
    }

    def source(self):
        # calling conan_basic_setup to enforce ABI
        tools.replace_in_file('OpenMesh/CMakeLists.txt', 'project (OpenMesh)', '''project (OpenMesh)
    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup()''')

        # do not set CMAKE_DEBUG_POSTFIX
        tools.replace_in_file('OpenMesh/CMakeLists.txt', 'set (CMAKE_DEBUG_POSTFIX "d")', '# set (CMAKE_DEBUG_POSTFIX "d")')

        # skip building document
        tools.replace_in_file('OpenMesh/CMakeLists.txt', 'add_subdirectory (Doc)', '# add_subdirectory (Doc)')

        # set ACG_PROJECT_BINDIR to bin for Windows
        tools.replace_in_file('OpenMesh/cmake/ACGCommon.cmake', 'set (ACG_PROJECT_BINDIR ".")', 'set (ACG_PROJECT_BINDIR "bin")')

        # do not build static target for non-Windows
        tools.replace_in_file('OpenMesh/src/OpenMesh/Tools/CMakeLists.txt', 'target_link_libraries (OpenMeshToolsStatic OpenMeshCoreStatic)', '# target_link_libraries (OpenMeshToolsStatic OpenMeshCoreStatic)')
        tools.replace_in_file('OpenMesh/src/OpenMesh/Tools/CMakeLists.txt', 'add_dependencies (fixbundle OpenMeshToolsStatic)', '# add_dependencies (fixbundle OpenMeshToolsStatic)')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_APPS'] = 'OFF'
        cmake.configure(source_folder='OpenMesh')
        return cmake

    def build(self):
        # choose shared/static for Windows builds
        tools.replace_in_file('OpenMesh/CMakeLists.txt', 'set( OPENMESH_BUILD_SHARED false', 'set( OPENMESH_BUILD_SHARED ' + ('true' if self.options.shared else 'false'))

        # do not build both shared and static library for non-Windows builds
        tools.replace_in_file('OpenMesh/src/OpenMesh/Core/CMakeLists.txt', 'SHAREDANDSTATIC', 'SHARED' if self.options.shared else 'STATIC')
        tools.replace_in_file('OpenMesh/src/OpenMesh/Tools/CMakeLists.txt', 'SHAREDANDSTATIC', 'SHARED' if self.options.shared else 'STATIC')

        cmake = self._configure_cmake()
        cmake.build()

        # run unit tests after the build
        cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if self.settings.os == 'Windows':
            # this is required by OpenMesh/Core/System/compiler.hh
            self.cpp_info.defines += ['_USE_MATH_DEFINES']
            if self.options.shared:
                # this is required for OPENMESHDLLEXPORT
                self.cpp_info.defines += ['OPENMESHDLL']
        self.cpp_info.libs = tools.collect_libs(self)
