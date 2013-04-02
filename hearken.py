#!/usr/bin/env python

from glob import glob
from jinja2 import Environment, FileSystemLoader
import yaml,shutil,re,codecs
from functools import partial
from markdown import markdown
trailing_slash = lambda x: x if x.endswith('/') else x+'/'

class Hearken(object):
    def __init__(self):
        self.template_dir = Environment(loader=FileSystemLoader('templates'))
        self.config       = yaml.load(file('config.yaml'))
        self.root_url     = trailing_slash(self.config['root_url']) 
        self.out_dir      = trailing_slash(self.config['path']) 
        shutil.rmtree(self.out_dir, ignore_errors=True)
        shutil.copytree('static',self.out_dir)
        self.load_posts()
        self.generate_indexes()
        map(self.generate_post,self.posts)


    title_sub = partial(re.compile(r'[^a-zA-Z0-9_\-]').sub, '')


    def load_posts(self):
        raw = (file(fn,'r').read().decode('utf8') for fn in glob('posts/*'))
        self.posts = []
        for post in raw:
            lines = post.split("\n",2)
            if len(lines)==3 and lines[0].startswith('#title') and lines[1].startswith('#date'):
                title = lines[0][6:].strip()
                date  = lines[1][5:].strip()
                post  = lines[2]
            else:
                continue
            file_name = self.title_sub(date)+'.html'
            print file_name
            self.posts.append(dict(title=title,date=date,post=post,html=markdown(post,extensions=['codehilite(guess_lang=False)']),link=file_name))
            self.posts.sort(lambda a,b: cmp(b['date'],a['date']))
        
    def render(self,name,**kwargs):
        return self.template_dir.get_template('/'+name+'.html').render(**kwargs)
    def generate_indexes(self):
        per = self.config['per_page']
        recent = self.posts[:self.config['recent_posts']]
        genFn = lambda i: 'index.html' if i==0 else 'index_%i.html'%(i/per)
        for i in xrange(0,len(self.posts),per):
            with codecs.open(self.out_dir+genFn(i),'w','utf-8') as fp:
                fp.write(self.render('index',
                    page=(i/per)+1,
                    pages=(len(self.posts)+per-1)/per,
                    prev=None if i==0 else genFn(i-per),next=None if i+per >=len(self.posts) else genFn(i+per),posts=self.posts[i:i+per],recent_posts=recent))
    def generate_post(self,post):
        with codecs.open(self.out_dir+post['link'],'w','utf-8') as fp:
            fp.write(self.render('post',post=post))
if __name__=='__main__':
    Hearken()

