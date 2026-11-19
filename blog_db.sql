SELECT * FROM posts;
SELECT * FROM contact;

INSERT INTO posts (title, slug, content, tagline, date, img_file) VALUES
('Welcome to My Blog', 'welcome-post', 'This is the first blog post on my site!', 'Getting Started', NOW(), 'welcome.jpg'),
('Flask Deployment Guide', 'flask-deployment', 'Step by step guide to deploy Flask apps on Render.', 'Deploy Flask Easily', NOW(), 'flask.jpg'),
('Python Tips and Tricks', 'python-tips', 'Some cool Python tricks for beginners and pros.', 'Code Smarter', NOW(), 'python.jpg'),
('Database Basics', 'db-basics', 'Learn the fundamentals of SQL and databases.', 'SQL 101', NOW(), 'database.jpg'),
('Understanding AI', 'ai-intro', 'An introduction to Artificial Intelligence concepts.', 'AI Simplified', NOW(), 'ai.jpg'),
('Web Development in 2025', 'webdev-2025', 'Trends and tools for modern web development.', 'Future of Web Dev', NOW(), 'webdev.jpg'),
('Cybersecurity Essentials', 'cybersecurity', 'Tips to stay safe online and protect your data.', 'Stay Safe Online', NOW(), 'cyber.jpg'),
('Machine Learning Project Ideas', 'ml-projects', '10 beginner-friendly ML project ideas.', 'ML for Starters', NOW(), 'ml.jpg'),
('Building REST APIs', 'rest-apis', 'Guide to creating REST APIs using Flask.', 'API Development', NOW(), 'api.jpg'),
('Final Thoughts', 'final-thoughts', 'Wrapping up with some personal thoughts on blogging.', 'Closing Notes', NOW(), 'final.jpg');


INSERT INTO posts (title, slug, content, tagline, date, img_file) VALUES
('Learning Flask Step by Step', 'flask-step-by-step', 'A beginner-friendly guide to Flask framework.', 'Flask Basics', NOW(), 'flask_basics.jpg'),
('Top 5 Python Libraries in 2025', 'python-libraries-2025', 'Exploring the most useful Python libraries this year.', 'Libraries You Need', NOW(), 'python_libs.jpg'),
('How to Use Git Effectively', 'git-guide', 'Tips for version control and collaboration with Git.', 'Master Git', NOW(), 'git.jpg'),
('SQL Joins Explained', 'sql-joins', 'A clear explanation of INNER, LEFT, RIGHT and FULL JOIN.', 'SQL Joins Made Simple', NOW(), 'joins.jpg'),
('What is Docker?', 'docker-intro', 'An introduction to containerization with Docker.', 'Docker Basics', NOW(), 'docker.jpg'),
('10 CSS Tricks Every Developer Should Know', 'css-tricks', 'Make your frontend beautiful with these CSS tips.', 'Frontend Tips', NOW(), 'css.jpg'),
('How to Build a Portfolio Website', 'portfolio-guide', 'Step by step guide to showcase your work online.', 'Build Your Brand', NOW(), 'portfolio.jpg'),
('Debugging in Python', 'debugging-python', 'How to use pdb and debugging tools in Python.', 'Fix Code Faster', NOW(), 'debug.jpg'),
('REST API vs GraphQL', 'rest-vs-graphql', 'Understanding the differences between REST and GraphQL.', 'API Comparison', NOW(), 'graphql.jpg'),
('Top 10 VS Code Extensions', 'vscode-extensions', 'Boost your productivity with these extensions.', 'VS Code Boost', NOW(), 'vscode.jpg'),
('Understanding Cloud Computing', 'cloud-intro', 'Basics of cloud platforms like AWS, GCP, and Azure.', 'Cloud Simplified', NOW(), 'cloud.jpg'),
('Deploy Django Apps', 'deploy-django', 'Step by step guide to deploying Django apps.', 'Django Deployment', NOW(), 'django.jpg'),
('API Authentication Methods', 'api-auth', 'Learn about JWT, OAuth2 and API key authentication.', 'Secure APIs', NOW(), 'auth.jpg'),
('Future of Artificial Intelligence', 'future-ai', 'Where AI is heading in the next decade.', 'AI Trends', NOW(), 'future_ai.jpg'),
('Learn HTML in 30 Minutes', 'html-30-mins', 'A crash course on HTML for beginners.', 'HTML Fast Track', NOW(), 'html.jpg'),
('How to Use Bootstrap 5', 'bootstrap5', 'Make responsive sites using Bootstrap 5.', 'Bootstrap Guide', NOW(), 'bootstrap.jpg'),
('SEO Tips for Beginners', 'seo-tips', 'How to make your website rank higher on Google.', 'SEO Basics', NOW(), 'seo.jpg'),
('Introduction to Linux Commands', 'linux-commands', 'Most used Linux commands for developers.', 'Linux 101', NOW(), 'linux.jpg'),
('How to Work with APIs in Python', 'python-apis', 'Learn how to consume REST APIs using Python.', 'APIs with Python', NOW(), 'apis.jpg'),
('Getting Started with Pandas', 'pandas-intro', 'Learn data analysis with Pandas library.', 'Data with Pandas', NOW(), 'pandas.jpg');
