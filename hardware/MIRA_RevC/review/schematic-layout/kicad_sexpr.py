import re
from pathlib import Path

def forms(s):
 depth=0;quote=False;escape=False;start=0;out=[]
 for i,c in enumerate(s):
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':
   if depth==0:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==0:out.append(s[start:i+1])
 assert depth==0 and not quote
 return out

def children(s):return forms(s[s.index('(')+1:s.rfind(')')])
def kind(s):return re.match(r'\(\s*([^\s()]+)',s)[1]
def child(s,k):return next((x for x in children(s) if kind(x)==k),None)
def quoted(s):return re.findall(r'"((?:\\.|[^"\\])*)"',s)
def prop(s,k):return next((quoted(x)[1] for x in children(s) if kind(x)=='property' and quoted(x)[0]==k),None)
def uuid(s):return quoted(child(s,'uuid'))[0]
def leaves(s,k):return [x for x in children(s) if kind(x)==k]
def replace_child(s,old,new):
 assert old in s
 return s.replace(old,new,1)
def walk(root):
 def rec(p,path,depth,name,page):
  s=p.read_text();u=uuid(s)
  yield dict(file=p,name=name,page=page,path=path,depth=depth,uuid=u,text=s)
  for sh in sorted(leaves(s,'sheet'),key=lambda sh:int(re.search(r'\(page "(\d+)"\)',sh)[1])):
   yield from rec(p.parent/prop(sh,'Sheetfile'),path+'/'+uuid(sh),depth+1,prop(sh,'Sheetname'),re.search(r'\(page "(\d+)"\)',sh)[1])
 return list(rec(root,'/'+uuid(root.read_text()),0,root.stem,'1'))
