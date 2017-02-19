import pipy
 
packpath = "pygeoj.py"
pipy.define_upload(packpath,
                   author="Karim Bahgat",
                   author_email="karim.bahgat.norway@gmail.com",
                   license="MIT",
                   name="PyGeoj",
                   changes=["Fixed more robust validation to avoid unexpected errors",
                            "Added skiperror option",
                            "Fixed feat type missing when add_feature()",
                            "Fixed crs not saving",
                            "Added fixerror option when loading and validating",
                            "Fix bug to allow null geometries and empty properties, and correctly represent them in json as null"],
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
pipy.upload(packpath)

