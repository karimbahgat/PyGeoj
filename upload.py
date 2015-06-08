import pypi
 
packpath = "pygeoj.py"
pypi.define_upload(packpath,
                   author="Karim Bahgat",
                   author_email="karim.bahgat.norway@gmail.com",
                   license="MIT",
                   name="PyGeoj",
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

pypi.generate_docs(packpath)
#pypi.upload_test(packpath)
pypi.upload(packpath)

