"""Top-level S-expression spans, preserving untouched KiCad text byte-for-byte."""
import re,json
def quote(s):return json.dumps(str(s),ensure_ascii=False)
def children(s):
 depth=0;quoted=False;escaped=False;start=None
 for i,ch in enumerate(s):
  if quoted:
   if escaped:escaped=False
   elif ch=='\\':escaped=True
   elif ch=='"':quoted=False
   continue
  if ch=='"':quoted=True
  elif ch=='(':
   depth+=1
   if depth==2:start=i
  elif ch==')':
   if depth==2:yield start,i+1,s[start:i+1]
   depth-=1
 assert depth==0 and not quoted

def reference(node):
 m=re.search(r'\(property\s+"Reference"\s+"([^"]+)"',node)
 return m[1] if m else None
