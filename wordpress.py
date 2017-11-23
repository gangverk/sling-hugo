import toml
import mistune
import glob
import os
import aniso8601
import mimetypes
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts

#wp = Client('http://getsling.com/xmlrpc.php', 'sling', 'pfKs58tq4&ew)xyQ#EH74qm@')
wp = Client('http://getsling.com/blog/xmlrpc.php', 'sling', '2j$tZBGEHiMilqF4kTXtV8no')


image_files = set()
uploaded_images = dict()

for filename in glob.glob("static/forestryio/images/*"):
    image_files.add(filename)

def upload_image(src):
    filename = src.replace('/blog/', 'static/')
 
    if filename in image_files:
        uploaded = uploaded_images.get(filename)
        if not uploaded:

            data = dict(name=os.path.split(filename)[-1],
                        type=mimetypes.guess_type(filename)[0])
            with open(filename, 'rb') as img:
                data['bits'] = xmlrpc_client.Binary(img.read())
            uploaded = wp.call(media.UploadFile(data))
            if uploaded:
                uploaded_images[filename] = uploaded
            else:
                print "Failed to upload image", src
        return uploaded
    print "failed"
    return None


class ImageRenderer(mistune.Renderer):
    def image(self, src, title, alt_text):
        uploaded_image = upload_image(src)
        if uploaded_image:
            src = uploaded_image['url']
        return super(ImageRenderer, self).image(src, title, alt_text)

markdown = mistune.Markdown(renderer=ImageRenderer())

for filename in glob.glob('content/post/*.md'):
    with open(filename, 'r') as content_file:
        content = content_file.read()
        if content.startswith("+++"):
            sections = content.split("+++")
            if len(sections) == 3:
                front_matter = toml.loads(sections[1])
                post = WordPressPost()

                post.title = front_matter.get("title")
                post.excerpt = front_matter.get("description")
                post.slug = filename.replace('content/post/','').replace('.md','')
                post.content = markdown(sections[2])

                wp_tags = front_matter.get("tags")
                if wp_tags:
                    post.terms_names = {'category': wp_tags}

                wp_date = front_matter.get("date")
                if wp_date:
                    post.date = aniso8601.parse_datetime(wp_date)

                wp_thumb = front_matter.get('image')
                if wp_thumb:
                    uploaded_image = upload_image(wp_thumb)
                    if uploaded_image:
                        post.thumbnail = uploaded_image['id']
                if not front_matter.get("draft"):
                    post.post_status = 'publish'

                print "posting", post.slug
                wp.call(NewPost(post))
    os.remove(filename)
print """
All done. Run the following to get deleted md files back
git ls-files --deleted | xargs git checkout --
"""
