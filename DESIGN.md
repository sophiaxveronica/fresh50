# fresh
Fresh: A CS50 Final Project
by Sophia Clark and Veronica Nutting

When first conceptualizing our project we wanted to focus on dynamic and appealing UI and UX while keeping a highly functional
website. In terms of design, we began our website using C$50 Finance, essentially using databases, tables and posts to create the
skeleton of our project. We wanted to create a sleek website that wouldn't be overwhelming for a freshman simply looking for advice
or upcoming events – we wanted to present a lot of information in easily digestable chunks.

To further ease the user experience we ensured that the website handled any lack of content by using "if statements" in our Python
code to ensure that our site couldn't be destabilized, despite our website being built with the intention of handling content
everywhere. In our original skeleton we created tables with foreign keys to optimize our queries: "categories", "languages", "posts"
and "users". We then gave options to users to view posts either "by Category", "by Language" or "by PAF" creating an extremely
straightforward interface that clearly presented the necessary information. While desiging, we wanted to create particularly
user-friendly error situations ensuring the site retained a pleasant UX. Other UX improvement efforts we made were done by sorting
events by the time they were posted and different users alphabetically. To create these different post viewing options we worked
using SQL queries, jinja and python.

We decided for our home page to be the events page as design-wise we found the most pleasant interaction a user could have would
be to be greeted by upcoming events when looking for advice from PAFs. Moreover as our sidebar always remains available, the
user could easily orient themself wherever they wanted to on the next click.

As we continued to develop our website, we wanted to incorporate a second interface that would be used by logged-in users (PAFs and
the FDO). We designed this second interface to incorporate new tabs that would only appear when a user is logged-in: the option to
add posts, add events, view user's posts and view the website's usage statistics. To this we also relied on sequel queries, jinja
and python.

In our day and age we must consider the necessity of having websites that are accessible on mobile devices. It is unrealistic to
consider that a non mobile-friendly website could be an effective tool, therefore we worked to design a website that could be
easily accessible on a much smaller device while keeping appealing UI and UX which also have a large impact on the accessibility
of the website.

Redesigning our website from the CS50 HTML bootstrap layout was also a key effort in our goal of designing a site with optimized UI
and UX. Using w3.css templates, we redesigned a website with an everpresent sidebar so that a user would always be able to reorient
themself to other tabs, and that the homebutton would always be available so that the user could return back to the beginning.
Aesthetically, we wanted a color template similar to Harvard's traditional crimson and white, yet we hoped to create a more modern
looking site with a clean interface. We chose to use w3.css as it is a framework using css with "built-in responsiveness",
which we found was critical for us to format our site as we wanted to style-wise, while still incorporating the necessities
needed in the functionality of the HTML.
