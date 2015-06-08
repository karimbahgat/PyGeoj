import gitdoc

FILENAME = "pygeoj"
FOLDERPATH = r"C:\Users\BIGKIMO\Github\PyGeoj"
OUTPATH = r"C:\Users\BIGKIMO\Github\PyGeoj"
OUTNAME = "README"
EXCLUDETYPES = ["variable","module"]
gitdoc.DocumentModule(FOLDERPATH,
                  filename=FILENAME,
                  outputfolder=OUTPATH,
                  outputname=OUTNAME,
                  excludetypes=EXCLUDETYPES,
                  )
