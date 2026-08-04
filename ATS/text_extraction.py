'''
this file deals with the 
1.Secure TempFile Staging 
2.Format Router
3. Coordinate Sorting & Text Extraction 
4.Text Normalization Layer
5.Return Clean Raw Text String
'''

import pymupdf
import pymupdf.layout  
import pymupdf4llm
import json

class TextExtraction:
    def __init__(self):
