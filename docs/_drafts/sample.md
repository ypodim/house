---
layout: post
title:  "hello world!"
date:   2020-02-02 00:38:50 -0800
categories: jekyll update
---
My year's resolution is to do a better job documenting my work with pictures, snippets and abandoned ideas. This site will serve both as the means and the end of my first post. 

I decided to go with a combination of [static content][static-content] with dynamic data served from a [VM][VM]. It's a little more complicated, but it's a fun project to try out. The Github Pages is as an easy way to publish back-of-the-envelope ideas, but most of my projects require a DB of some sort, hence the need for the VM. I could've used a VM for everything and that might be a way to consolidate things in the future, but, for now, I like not having to worry about server maintenance for the static content.

I'm not a big fun of `gems` and `ruby`, but I [jekyll][jekyll]'s structure and the separation between posts and pages.
You’ll find this post in your `_posts` directory. Go ahead and edit it and re-build the site to see your changes. You can rebuild the site in many different ways, but the most common way is to run `jekyll serve`, which launches a web server and auto-regenerates your site when a file is updated.

Jekyll requires blog post files to be named according to the following format:

`YEAR-MONTH-DAY-title.MARKUP`

Where `YEAR` is a four-digit number, `MONTH` and `DAY` are both two-digit numbers, and `MARKUP` is the file extension representing the format used in the file. After that, include the necessary front matter. Take a look at the source for this post to get an idea about how it works.

Jekyll also offers powerful support for code snippets:

{% highlight ruby %}
def print_hi(name)
  puts "Hi, #{name}"
end
print_hi('Tom')
#=> prints 'Hi, Tom' to STDOUT.
{% endhighlight %}


[static-content]: https://pages.github.com/
[VN]: https://www.a2hosting.com/
[jekyll]: https://jekyllrb.com/
