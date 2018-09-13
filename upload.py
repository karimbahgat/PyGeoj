import pipy
 
packpath = "pygeoj.py"
pipy.define_upload(packpath,
                   author="Karim Bahgat",
                   author_email="karim.bahgat.norway@gmail.com",
                   license="MIT",
                   name="PyGeoj",
                   changes=["Bump to stable version",
                            "Officially support Python 3"],
                   description="A simple Python GeoJSON file reader and writer.",
                   url="http://github.com/karimbahgat/PyGeoj",
                   keywords="GIS spatial file format GeoJSON",
                   classifiers=["License :: OSI Approved",
                                "Programming Language :: Python",
                                "Development Status :: 4 - Beta",
                                "Intended Audience :: Developers",
                                "Intended Audience :: Science/Research",
                                'Intended Audience :: End Users/Desktop',
                                "Topic :: Scientific/Engineering :: GIS"],
                   )

pipy.generate_docs(packpath)
#pipy.upload_test(packpath)
#pipy.upload(packpath)

