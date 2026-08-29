# Canvas LMS REST API -- Practical Reference for Course Management

A comprehensive reference for building and managing an entire Canvas course programmatically. All endpoints are relative to `https://<your-canvas-domain>/api/v1/`.

**Base URL pattern**: `https://byu.instructure.com/api/v1/` (for BYU)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limits and Pagination](#rate-limits-and-pagination)
3. [Course Setup](#1-course-setup)
4. [Tabs / Navigation](#2-tabs--navigation)
5. [Modules](#3-modules)
6. [Module Items](#4-module-items)
7. [Assignment Groups](#5-assignment-groups)
8. [Assignments](#6-assignments)
9. [Pages](#7-pages)
10. [Quizzes (Classic)](#8-quizzes-classic)
11. [New Quizzes](#9-new-quizzes)
12. [Discussions](#10-discussions)
13. [Files and Folders](#11-files-and-folders)
14. [Announcements](#12-announcements)
15. [Calendar Events](#13-calendar-events)
16. [Rubrics](#14-rubrics)
17. [Grades and Submissions](#15-grades-and-submissions)
18. [Users, Enrollments, Sections, Groups](#16-users-enrollments-sections-groups)
19. [Outcomes](#17-outcomes)
20. [Blueprint Courses](#18-blueprint-courses)
21. [Content Migrations and Exports](#19-content-migrations-and-exports)
22. [Analytics](#20-analytics)
23. [Conversations / Messaging](#21-conversations--messaging)
24. [The GraphQL API](#the-graphql-api)
25. [Webhooks and Canvas Data](#webhooks-and-canvas-data)
26. [Notable Limitations](#notable-limitations)

---

## Authentication

### Personal Access Token (simplest for a single professor)

1. Go to **Account > Settings** in Canvas
2. Under "Approved Integrations," click **+ New Access Token**
3. Give it a name and optional expiration date
4. Copy the token immediately (it is shown only once)

Use it in every request:

```
Authorization: Bearer <YOUR_TOKEN>
```

Or as a query parameter (less secure): `?access_token=<YOUR_TOKEN>`

### OAuth2 (for multi-user apps)

Three-step flow:
1. Register a **Developer Key** with your Canvas admin
2. Redirect users to `GET /login/oauth2/auth?client_id=XXX&response_type=code&redirect_uri=YYY`
3. Exchange the authorization code at `POST /login/oauth2/token`

Access tokens expire after **1 hour**; use the refresh token to get new ones without re-authorization.

**For a professor managing their own course**: a personal access token is all you need.

### Token Scopes

When creating a developer key, you can restrict tokens to specific API scopes (e.g., only allow reading enrollments). Personal tokens inherit the user's full permissions.

---

## Rate Limits and Pagination

### Rate Limits

Canvas uses **dynamic throttling** rather than a fixed requests-per-minute limit.

- Each request has a **cost** (returned in the `X-Request-Cost` header)
- Your remaining quota is in `X-Rate-Limit-Remaining`
- Quota replenishes continuously -- sequential requests rarely trigger limits
- Parallel requests incur a **pre-flight penalty** (credited back on completion)
- Exceeding the limit returns **HTTP 403** with a `Rate Limit Exceeded` message

**Best practices**:
- Make requests sequentially when possible
- Implement retry logic with exponential backoff on 403
- Each access token has an independent quota

### Pagination

- Default page size: **10 items** per request
- Adjust with `?per_page=50` (max varies, typically 100)
- Canvas returns a `Link` HTTP header with URLs for `next`, `prev`, `first`, `last` pages

```
Link: <https://...?page=2&per_page=50>; rel="next",
      <https://...?page=5&per_page=50>; rel="last"
```

**Always follow the `Link` header** to iterate through pages. The URLs are complete and include all necessary parameters.

---

## 1. Course Setup

### Read / Update Course Settings

| Action | Method | Endpoint |
|--------|--------|----------|
| Get course details | `GET` | `/courses/:course_id` |
| Update course | `PUT` | `/courses/:course_id` |
| Get course settings | `GET` | `/courses/:course_id/settings` |
| Update course settings | `PUT` | `/courses/:course_id/settings` |

### Key Parameters for `PUT /courses/:id`

```
course[name]                         # Course name
course[course_code]                  # Short name / code
course[default_view]                 # "feed", "modules", "assignments", "syllabus"
course[syllabus_body]                # HTML syllabus content
course[syllabus_course_summary]      # Show course summary on syllabus page (bool)
course[image_id]                     # File ID for course image (card image)
course[image_url]                    # URL for course image
course[time_zone]                    # Course timezone
course[hide_final_grades]            # Hide grade totals from students (bool)
course[apply_assignment_group_weights] # Enable weighted assignment groups (bool)
course[event]                        # "offer" (publish), "claim" (unpublish), "conclude", "delete"
course[restrict_enrollments_to_course_dates] # bool
course[start_at]                     # Course start date
course[end_at]                       # Course end date
```

### Course Settings (`PUT /courses/:id/settings`)

```
hide_distribution_graphs             # Hide grade distribution from students
lock_all_announcements               # Prevent replies on announcements
restrict_student_past_view           # Hide past content
restrict_student_future_view         # Hide future content
show_announcements_on_home_page      # bool
home_page_announcement_limit         # Number of announcements on home page
```

### Publish / Unpublish a Course

```
PUT /courses/:id
  course[event]=offer    # Publish
  course[event]=claim    # Unpublish
```

### Preview HTML

```
POST /courses/:course_id/preview_html
  html=<p>Test</p>
```

Returns processed HTML (resolves links, etc.) -- useful for testing before committing content.

---

## 2. Tabs / Navigation

| Action | Method | Endpoint |
|--------|--------|----------|
| List all tabs | `GET` | `/courses/:course_id/tabs` |
| Update a tab | `PUT` | `/courses/:course_id/tabs/:tab_id` |

### Tab IDs (common ones)

`home`, `announcements`, `assignments`, `discussions`, `grades`, `people`, `pages`, `files`, `syllabus`, `outcomes`, `quizzes`, `modules`, `conferences`, `collaborations`, `settings`

### Show / Hide a Tab

```
PUT /courses/:course_id/tabs/:tab_id
  hidden=true    # Hide from students (still visible to teachers)
  hidden=false   # Show to students
```

### Reorder Tabs

```
PUT /courses/:course_id/tabs/:tab_id
  position=3     # 1-based position
```

**Limitation**: The `Home` and `Settings` tabs cannot be hidden or moved.

---

## 3. Modules

| Action | Method | Endpoint |
|--------|--------|----------|
| List modules | `GET` | `/courses/:id/modules` |
| Get one module | `GET` | `/courses/:id/modules/:module_id` |
| Create module | `POST` | `/courses/:id/modules` |
| Update module | `PUT` | `/courses/:id/modules/:module_id` |
| Delete module | `DELETE` | `/courses/:id/modules/:module_id` |

### Create a Module

```
POST /courses/:id/modules
  module[name]=Week 1 - Introduction
  module[position]=1
  module[unlock_at]=2026-01-12T00:00:00Z       # Lock until this date
  module[require_sequential_progress]=true       # Students must complete items in order
  module[prerequisite_module_ids][]=123          # Must complete module 123 first
  module[publish_final_grade]=false              # Post grade when module completed
```

### Publish / Unpublish

```
PUT /courses/:id/modules/:module_id
  module[published]=true
```

### Reorder Modules

Set `module[position]=N` on each module via `PUT`. Position is 1-based.

### Prerequisites

```
PUT /courses/:id/modules/:module_id
  module[prerequisite_module_ids][]=101
  module[prerequisite_module_ids][]=102
```

---

## 4. Module Items

| Action | Method | Endpoint |
|--------|--------|----------|
| List items | `GET` | `/courses/:id/modules/:mod_id/items` |
| Get one item | `GET` | `/courses/:id/modules/:mod_id/items/:item_id` |
| Create item | `POST` | `/courses/:id/modules/:mod_id/items` |
| Update item | `PUT` | `/courses/:id/modules/:mod_id/items/:item_id` |
| Delete item | `DELETE` | `/courses/:id/modules/:mod_id/items/:item_id` |

### Item Types and Required Fields

| Type | `content_id` required? | Notes |
|------|----------------------|-------|
| `Page` | No | Use `page_url` (the slug) instead |
| `Assignment` | Yes | Assignment ID |
| `Quiz` | Yes | Quiz ID |
| `Discussion` | Yes | Discussion topic ID |
| `File` | Yes | File ID |
| `ExternalUrl` | No | Use `external_url` |
| `ExternalTool` | No | Use `external_url` for the tool launch URL |
| `SubHeader` | No | Text divider, `title` only |

### Create Examples

**Add a page**:
```
POST /courses/:id/modules/:mod_id/items
  module_item[type]=Page
  module_item[page_url]=week-1-overview
  module_item[position]=1
```

**Add an external URL**:
```
POST /courses/:id/modules/:mod_id/items
  module_item[type]=ExternalUrl
  module_item[title]=McKinsey Problem Solving Article
  module_item[external_url]=https://example.com/article
  module_item[new_tab]=true
```

**Add a sub-header**:
```
POST /courses/:id/modules/:mod_id/items
  module_item[type]=SubHeader
  module_item[title]=--- Readings ---
```

### Completion Requirements

```
module_item[completion_requirement][type]=must_view
module_item[completion_requirement][type]=must_submit
module_item[completion_requirement][type]=must_contribute
module_item[completion_requirement][type]=must_mark_done
module_item[completion_requirement][type]=min_score
module_item[completion_requirement][min_score]=80
```

| Requirement | Valid For |
|------------|-----------|
| `must_view` | All types |
| `must_submit` | Assignment, Quiz |
| `must_contribute` | Assignment, Discussion, Page |
| `must_mark_done` | Assignment, Page |
| `min_score` | Assignment, Quiz |

### Publish / Unpublish an Item

```
PUT /courses/:id/modules/:mod_id/items/:item_id
  module_item[published]=true
```

### Move Item to Another Module

```
PUT /courses/:id/modules/:mod_id/items/:item_id
  module_item[module_id]=456    # Target module ID
```

### Indent Items

```
module_item[indent]=0   # No indent (default)
module_item[indent]=1   # One level
module_item[indent]=2   # Two levels
```

---

## 5. Assignment Groups

| Action | Method | Endpoint |
|--------|--------|----------|
| List groups | `GET` | `/courses/:id/assignment_groups` |
| Get one group | `GET` | `/courses/:id/assignment_groups/:group_id` |
| Create group | `POST` | `/courses/:id/assignment_groups` |
| Update group | `PUT` | `/courses/:id/assignment_groups/:group_id` |
| Delete group | `DELETE` | `/courses/:id/assignment_groups/:group_id` |

### Create with Weights and Drop Rules

```
POST /courses/:id/assignment_groups
  name=Quizzes
  position=2
  group_weight=20                           # 20% of total grade
  rules[drop_lowest]=1                      # Drop lowest 1 score
  rules[drop_highest]=0                     # Drop highest 0 scores
  rules[never_drop][]=assignment_id_1       # Never drop this assignment
  rules[never_drop][]=assignment_id_2
```

**Remember**: You must also enable weighted groups on the course:
```
PUT /courses/:id
  course[apply_assignment_group_weights]=true
```

### On Deletion

Use `move_assignments_to=OTHER_GROUP_ID` to move assignments to another group instead of deleting them:
```
DELETE /courses/:id/assignment_groups/:group_id?move_assignments_to=789
```

---

## 6. Assignments

| Action | Method | Endpoint |
|--------|--------|----------|
| List assignments | `GET` | `/courses/:id/assignments` |
| Get one assignment | `GET` | `/courses/:id/assignments/:assignment_id` |
| Create assignment | `POST` | `/courses/:id/assignments` |
| Update assignment | `PUT` | `/courses/:id/assignments/:assignment_id` |
| Delete assignment | `DELETE` | `/courses/:id/assignments/:assignment_id` |
| Duplicate assignment | `POST` | `/courses/:id/assignments/:assignment_id/duplicate` |
| Bulk update dates | `PUT` | `/courses/:id/assignments/bulk_update` |

### Create a Full Assignment

```
POST /courses/:id/assignments
  assignment[name]=Case Analysis: Muscle Cola
  assignment[description]=<h2>Instructions</h2><p>Analyze the cost structure...</p>
  assignment[assignment_group_id]=123
  assignment[points_possible]=100
  assignment[grading_type]=points              # points, percent, letter_grade, gpa_scale, pass_fail, not_graded
  assignment[due_at]=2026-03-20T23:59:00Z
  assignment[unlock_at]=2026-03-13T00:00:00Z
  assignment[lock_at]=2026-03-21T23:59:00Z
  assignment[submission_types][]=online_upload
  assignment[submission_types][]=online_text_entry
  assignment[allowed_extensions][]=pdf
  assignment[allowed_extensions][]=docx
  assignment[published]=true
  assignment[position]=1
  assignment[allowed_attempts]=3               # -1 for unlimited
  assignment[omit_from_final_grade]=false
  assignment[notify_of_update]=false
```

### Submission Types

```
online_upload          # File upload
online_text_entry      # Rich text editor
online_url             # URL submission
media_recording        # Audio/video recording
student_annotation     # Annotate a document
on_paper               # In-person, no online submission
external_tool          # LTI tool (e.g., New Quizzes, Turnitin)
online_quiz            # Classic Canvas quiz
discussion_topic       # Graded discussion
none                   # No submission (e.g., attendance)
```

### Peer Review

```
assignment[peer_reviews]=true
assignment[automatic_peer_reviews]=true
assignment[peer_review_count]=2
assignment[peer_reviews_assign_at]=2026-03-25T23:59:00Z
assignment[anonymous_peer_reviews]=true
assignment[intra_group_peer_reviews]=false
```

### Group Assignments

```
assignment[group_category_id]=456              # ID of the group set
assignment[grade_group_students_individually]=false
```

### Turnitin / Plagiarism Detection

```
assignment[turnitin_enabled]=true
assignment[turnitin_settings][originality_report_visibility]=after_grading
assignment[turnitin_settings][s_paper_check]=true           # Check against student papers
assignment[turnitin_settings][internet_check]=true          # Check against internet
assignment[turnitin_settings][journal_check]=true           # Check against journals
assignment[turnitin_settings][exclude_biblio]=true
assignment[turnitin_settings][exclude_quoted]=true
assignment[turnitin_settings][exclude_small_matches_type]=percent
assignment[turnitin_settings][exclude_small_matches_value]=10
```

### External Tool (LTI) Assignment

```
assignment[submission_types][]=external_tool
assignment[external_tool_tag_attributes][url]=https://tool.example.com/launch
assignment[external_tool_tag_attributes][new_tab]=true
```

### Moderated Grading

```
assignment[moderated_grading]=true
assignment[grader_count]=2
assignment[final_grader_id]=user_id
assignment[anonymous_grading]=true
```

### Assignment Overrides (per-section or per-student dates)

```
POST /courses/:id/assignments/:assignment_id/overrides
  assignment_override[title]=Section 001 Override
  assignment_override[course_section_id]=789
  assignment_override[due_at]=2026-03-22T23:59:00Z
  assignment_override[unlock_at]=2026-03-15T00:00:00Z
  assignment_override[lock_at]=2026-03-23T23:59:00Z
```

Can also override by `student_ids[]` or `group_id`.

---

## 7. Pages

| Action | Method | Endpoint |
|--------|--------|----------|
| List pages | `GET` | `/courses/:id/pages` |
| Get front page | `GET` | `/courses/:id/front_page` |
| Set front page | `PUT` | `/courses/:id/front_page` |
| Create page | `POST` | `/courses/:id/pages` |
| Get page | `GET` | `/courses/:id/pages/:url_or_id` |
| Update page | `PUT` | `/courses/:id/pages/:url_or_id` |
| Delete page | `DELETE` | `/courses/:id/pages/:url_or_id` |
| Duplicate page | `POST` | `/courses/:id/pages/:url_or_id/duplicate` |
| List revisions | `GET` | `/courses/:id/pages/:url_or_id/revisions` |
| Revert to revision | `POST` | `/courses/:id/pages/:url_or_id/revisions/:revision_id` |

### Create a Page with HTML Content

```
POST /courses/:id/pages
  wiki_page[title]=Week 3: Think Clearly
  wiki_page[body]=<h2>Learning Objectives</h2><p>By the end of this week...</p>
  wiki_page[published]=true
  wiki_page[front_page]=false
  wiki_page[editing_roles]=teachers            # "teachers", "students", "members", "public"
  wiki_page[notify_of_update]=false
  wiki_page[publish_at]=2026-03-16T08:00:00Z   # Scheduled publish
```

### Embedding Quarto-Rendered HTML

Since `wiki_page[body]` accepts arbitrary HTML, you can render a `.qmd` file to HTML and push it directly:

```bash
quarto render chapter.qmd --to html --no-header
# Extract the <body> content and POST it as wiki_page[body]
```

The HTML will be rendered by Canvas. Note: Canvas sanitizes some HTML/JS. Inline styles and standard tags work; `<script>` tags and iframes (except whitelisted domains) are stripped.

### Page Slugs

Pages are identified by URL slug (e.g., `week-3-think-clearly`) or numeric ID. Canvas auto-generates the slug from the title.

---

## 8. Quizzes (Classic)

**Note**: Classic Quizzes are the older quiz engine. Many institutions are migrating to New Quizzes (see next section). Classic Quizzes have full API support.

| Action | Method | Endpoint |
|--------|--------|----------|
| List quizzes | `GET` | `/courses/:id/quizzes` |
| Get quiz | `GET` | `/courses/:id/quizzes/:quiz_id` |
| Create quiz | `POST` | `/courses/:id/quizzes` |
| Update quiz | `PUT` | `/courses/:id/quizzes/:quiz_id` |
| Delete quiz | `DELETE` | `/courses/:id/quizzes/:quiz_id` |
| Reorder items | `POST` | `/courses/:id/quizzes/:quiz_id/reorder` |

### Create a Quiz

```
POST /courses/:id/quizzes
  quiz[title]=Quiz 5: MECE Frameworks
  quiz[quiz_type]=assignment                    # assignment, practice_quiz, graded_survey, survey
  quiz[description]=<p>Test your understanding of...</p>
  quiz[time_limit]=30                           # Minutes (null for no limit)
  quiz[shuffle_answers]=true
  quiz[hide_results]=null                       # null (show), "always", "until_after_last_attempt"
  quiz[show_correct_answers]=true
  quiz[show_correct_answers_at]=2026-03-21T00:00:00Z
  quiz[hide_correct_answers_at]=2026-04-01T00:00:00Z
  quiz[allowed_attempts]=2                      # -1 for unlimited
  quiz[scoring_policy]=keep_highest             # keep_highest, keep_latest, keep_average
  quiz[one_question_at_a_time]=false
  quiz[cant_go_back]=false                      # Lock questions after answering
  quiz[access_code]=SECRET123                   # Password to start quiz
  quiz[ip_filter]=192.168.1.0/24               # IP restriction
  quiz[due_at]=2026-03-20T23:59:00Z
  quiz[lock_at]=2026-03-21T23:59:00Z
  quiz[unlock_at]=2026-03-13T00:00:00Z
  quiz[published]=false
  quiz[assignment_group_id]=123
```

### Quiz Questions

| Action | Method | Endpoint |
|--------|--------|----------|
| List questions | `GET` | `/courses/:id/quizzes/:quiz_id/questions` |
| Get question | `GET` | `/courses/:id/quizzes/:quiz_id/questions/:question_id` |
| Create question | `POST` | `/courses/:id/quizzes/:quiz_id/questions` |
| Update question | `PUT` | `/courses/:id/quizzes/:quiz_id/questions/:question_id` |
| Delete question | `DELETE` | `/courses/:id/quizzes/:quiz_id/questions/:question_id` |

### Question Types

- `multiple_choice_question`
- `true_false_question`
- `short_answer_question` (fill in the blank)
- `fill_in_multiple_blanks_question`
- `multiple_answers_question` (select all that apply)
- `multiple_dropdowns_question`
- `matching_question`
- `numerical_question`
- `calculated_question`
- `essay_question`
- `file_upload_question`
- `text_only_question` (informational, not scored)

### Create a Multiple Choice Question

```
POST /courses/:id/quizzes/:quiz_id/questions
  question[question_name]=MECE Definition
  question[question_text]=<p>What does MECE stand for?</p>
  question[question_type]=multiple_choice_question
  question[points_possible]=5
  question[position]=1
  question[correct_comments]=Correct!
  question[incorrect_comments]=Review Chapter 5.
  question[answers][0][answer_text]=Mutually Exclusive, Collectively Exhaustive
  question[answers][0][answer_weight]=100
  question[answers][1][answer_text]=Most Effective, Cost Efficient
  question[answers][1][answer_weight]=0
  question[answers][2][answer_text]=Multiple Entries, Complete Evaluation
  question[answers][2][answer_weight]=0
```

### Question Groups (Random Question Pools)

| Action | Method | Endpoint |
|--------|--------|----------|
| List groups | `GET` | `/courses/:id/quizzes/:quiz_id/groups` |
| Create group | `POST` | `/courses/:id/quizzes/:quiz_id/groups` |
| Update group | `PUT` | `/courses/:id/quizzes/:quiz_id/groups/:group_id` |
| Delete group | `DELETE` | `/courses/:id/quizzes/:quiz_id/groups/:group_id` |
| Reorder questions | `POST` | `/courses/:id/quizzes/:quiz_id/groups/:group_id/reorder` |

```
POST /courses/:id/quizzes/:quiz_id/groups
  quiz_group[name]=Random Pool: Chapter 5
  quiz_group[pick_count]=5                     # Pick 5 random questions from this group
  quiz_group[question_points]=2                # Each worth 2 points
  quiz_group[assessment_question_bank_id]=789  # Pull from a question bank
```

### Quiz Submissions and Statistics

```
GET  /courses/:id/quizzes/:quiz_id/submissions          # List submissions
GET  /courses/:id/quizzes/:quiz_id/statistics            # Aggregate stats
POST /courses/:id/quizzes/:quiz_id/submissions           # Start a submission
PUT  /courses/:id/quizzes/:quiz_id/submissions/:sub_id   # Update (answer questions)
POST /courses/:id/quizzes/:quiz_id/submissions/:sub_id/complete  # Submit
```

---

## 9. New Quizzes

New Quizzes is an **LTI-based** quiz engine, separate from Classic Quizzes. Its API support is **severely limited** compared to Classic Quizzes.

### What you CAN do via REST API

- Create an assignment with `submission_types=["external_tool"]` pointing to the New Quizzes LTI URL
- The assignment shell appears in Canvas; the quiz content lives in the New Quizzes tool
- List assignments with `?new_quizzes=true` to filter

### What you CANNOT do via the public REST API

- Create or edit quiz questions
- Configure quiz settings (time limits, attempts, etc.)
- Manage question banks (item banks)
- Read quiz statistics

### New Quizzes API (separate service)

Instructure has a **separate New Quizzes API** (not part of the standard Canvas REST API) that requires additional authentication and is not publicly documented for general use. Some institutions may have access.

**Practical advice**: If you need full programmatic quiz management, use **Classic Quizzes** which have complete API coverage. If your institution requires New Quizzes, plan to create quiz content manually or via QTI import.

---

## 10. Discussions

| Action | Method | Endpoint |
|--------|--------|----------|
| List discussions | `GET` | `/courses/:id/discussion_topics` |
| Create discussion | `POST` | `/courses/:id/discussion_topics` |
| Update discussion | `PUT` | `/courses/:id/discussion_topics/:topic_id` |
| Delete discussion | `DELETE` | `/courses/:id/discussion_topics/:topic_id` |
| Reorder pinned | `POST` | `/courses/:id/discussion_topics/reorder` |
| Post entry | `POST` | `/courses/:id/discussion_topics/:topic_id/entries` |
| Post reply | `POST` | `/courses/:id/discussion_topics/:topic_id/entries/:entry_id/replies` |
| Get full thread | `GET` | `/courses/:id/discussion_topics/:topic_id/view` |

### Create a Discussion

```
POST /courses/:id/discussion_topics
  title=Case Discussion: Strategy Frameworks
  message=<p>After reading the Muscle Cola case, discuss...</p>
  discussion_type=threaded                     # "threaded", "side_comment", "not_threaded"
  published=true
  require_initial_post=true                    # Must post before seeing others
  pinned=false
  allow_rating=true
  only_graders_can_rate=false
  delayed_post_at=2026-03-20T08:00:00Z        # Schedule future post
  lock_at=2026-03-27T23:59:00Z                # Lock discussion at this date
```

### Create a Graded Discussion

```
POST /courses/:id/discussion_topics
  title=Graded: Networking Reflection
  message=<p>Reflect on your informational interviews...</p>
  discussion_type=threaded
  published=true
  assignment[name]=Graded: Networking Reflection
  assignment[points_possible]=20
  assignment[due_at]=2026-03-25T23:59:00Z
  assignment[grading_type]=points
  assignment[submission_types][]=discussion_topic
```

### Create an Announcement (via Discussion Topics API)

```
POST /courses/:id/discussion_topics
  title=Welcome to Week 8!
  message=<p>This week we focus on...</p>
  is_announcement=true
  published=true
  delayed_post_at=2026-03-16T08:00:00Z        # Schedule for future
  specific_sections=section_id_1               # Section-specific
```

---

## 11. Files and Folders

### Three-Step File Upload Process

**Step 1**: Notify Canvas

```
POST /courses/:course_id/files
  name=case-analysis-template.docx
  size=245760
  content_type=application/vnd.openxmlformats-officedocument.wordprocessingml.document
  parent_folder_path=Course Files/Templates
  on_duplicate=rename                          # "overwrite" or "rename"
```

Response returns `upload_url` and `upload_params`.

**Step 2**: Upload the file

```
POST <upload_url>
  <all fields from upload_params>
  file=@case-analysis-template.docx            # Must be the LAST field
```

Response: HTTP 301 redirect with `Location` header.

**Step 3**: Confirm upload

```
GET <Location header URL>
  Authorization: Bearer <token>
```

Returns the file object with `id`, `url`, `display_name`, etc.

### Folder Management

| Action | Method | Endpoint |
|--------|--------|----------|
| List folders | `GET` | `/courses/:id/folders` |
| Get folder by path | `GET` | `/courses/:id/folders/by_path/*full_path` |
| Create folder | `POST` | `/courses/:id/folders` |
| Update folder | `PUT` | `/folders/:folder_id` |
| Delete folder | `DELETE` | `/folders/:folder_id` |
| List files in folder | `GET` | `/folders/:folder_id/files` |
| Copy file | `POST` | `/folders/:dest_folder_id/copy_file` |

```
POST /courses/:id/folders
  name=Week 3 Materials
  parent_folder_path=Course Files
  hidden=false
  locked=false
```

### File Quota

```
GET /courses/:id/files/quota
```

Returns `quota` (bytes allowed) and `quota_used` (bytes consumed).

---

## 12. Announcements

### List Announcements

```
GET /announcements
  context_codes[]=course_12345
  start_date=2026-01-01
  end_date=2026-06-01
  active_only=true
  latest_only=true                             # One per course
```

### Create an Announcement

Announcements are created through the **Discussion Topics API** with `is_announcement=true`:

```
POST /courses/:id/discussion_topics
  title=Mid-Semester Update
  message=<h2>Important Updates</h2><p>Here are the key changes...</p>
  is_announcement=true
  published=true
  delayed_post_at=2026-03-20T08:00:00Z        # Schedule for later
  specific_sections=101,102                    # Target specific sections
```

### Lock Comments on Announcements

```
PUT /courses/:id/discussion_topics/:topic_id
  locked=true
```

---

## 13. Calendar Events

| Action | Method | Endpoint |
|--------|--------|----------|
| List events | `GET` | `/calendar_events` |
| Create event | `POST` | `/calendar_events` |
| Get event | `GET` | `/calendar_events/:id` |
| Update event | `PUT` | `/calendar_events/:id` |
| Delete event | `DELETE` | `/calendar_events/:id` |
| Set timetable | `POST` | `/courses/:id/calendar_events/timetable` |

### Create a Course Calendar Event

```
POST /calendar_events
  calendar_event[context_code]=course_12345
  calendar_event[title]=Guest Speaker: BCG Partner
  calendar_event[description]=<p>Join us for a talk on...</p>
  calendar_event[start_at]=2026-03-25T14:00:00Z
  calendar_event[end_at]=2026-03-25T15:30:00Z
  calendar_event[location_name]=TNRB 290
  calendar_event[location_address]=Provo, UT
```

### Recurring Events

```
calendar_event[rrule]=FREQ=WEEKLY;BYDAY=TU,TH;COUNT=28
```

Uses iCalendar RRULE syntax.

### Duplicate an Event

```
calendar_event[duplicate][count]=14
calendar_event[duplicate][interval]=1
calendar_event[duplicate][frequency]=weekly
```

### Appointment Groups (Office Hours / Time Slots)

```
POST /appointment_groups
  appointment_group[context_codes][]=course_12345
  appointment_group[title]=Office Hours
  appointment_group[sub_context_codes][]=course_section_101
  appointment_group[min_appointments_per_participant]=0
  appointment_group[max_appointments_per_participant]=1
  appointment_group[new_appointments][X][]=2026-03-25T14:00:00Z
  appointment_group[new_appointments][X][]=2026-03-25T14:30:00Z
```

---

## 14. Rubrics

| Action | Method | Endpoint |
|--------|--------|----------|
| List rubrics | `GET` | `/courses/:id/rubrics` |
| Get rubric | `GET` | `/courses/:id/rubrics/:rubric_id` |
| Create rubric | `POST` | `/courses/:id/rubrics` |
| Update rubric | `PUT` | `/courses/:id/rubrics/:rubric_id` |
| Delete rubric | `DELETE` | `/courses/:id/rubrics/:rubric_id` |
| Import CSV | `POST` | `/courses/:id/rubrics/upload` |
| Download template | `GET` | `/rubrics/upload_template` |

### Create a Rubric and Attach to Assignment

```
POST /courses/:id/rubrics
  rubric[title]=Consulting Deliverable Rubric
  rubric[free_form_criterion_comments]=false
  rubric[criteria][0][description]=Problem Definition
  rubric[criteria][0][points]=25
  rubric[criteria][0][ratings][0][description]=Exceptional
  rubric[criteria][0][ratings][0][points]=25
  rubric[criteria][0][ratings][1][description]=Proficient
  rubric[criteria][0][ratings][1][points]=20
  rubric[criteria][0][ratings][2][description]=Developing
  rubric[criteria][0][ratings][2][points]=10
  rubric[criteria][0][ratings][3][description]=Incomplete
  rubric[criteria][0][ratings][3][points]=0
  rubric[criteria][1][description]=Analysis Quality
  rubric[criteria][1][points]=25
  rubric[criteria][1][ratings][0][description]=Exceptional
  rubric[criteria][1][ratings][0][points]=25
  ...
  rubric_association[association_type]=Assignment
  rubric_association[association_id]=ASSIGNMENT_ID
  rubric_association[use_for_grading]=true
  rubric_association[purpose]=grading
```

### Rubric Associations

```
POST /courses/:id/rubric_associations
  rubric_association[rubric_id]=456
  rubric_association[association_type]=Assignment
  rubric_association[association_id]=789
  rubric_association[use_for_grading]=true
  rubric_association[purpose]=grading          # "grading" or "bookmark"
```

### Rubric Assessments (grading with rubric)

```
POST /courses/:id/rubric_associations/:assoc_id/rubric_assessments
  rubric_assessment[user_id]=student_id
  rubric_assessment[assessment_type]=grading
  rubric_assessment[criterion_CRITERION_ID][points]=20
  rubric_assessment[criterion_CRITERION_ID][comments]=Good analysis
```

---

## 15. Grades and Submissions

### Read Grades

```
# Single student, single assignment
GET /courses/:id/assignments/:assignment_id/submissions/:user_id

# All submissions for an assignment
GET /courses/:id/assignments/:assignment_id/submissions

# All submissions for a student across assignments
GET /courses/:id/students/submissions?student_ids[]=USER_ID

# Submission summary (counts)
GET /courses/:id/assignments/:assignment_id/submission_summary
```

### Post / Update a Grade

```
PUT /courses/:id/assignments/:assignment_id/submissions/:user_id
  submission[posted_grade]=85                  # Points
  submission[posted_grade]=85%                 # Percentage
  submission[posted_grade]=A-                  # Letter grade
  submission[excuse]=true                      # Excuse student
  comment[text_comment]=Great work on the MECE framework
```

### Bulk Grade Update

```
POST /courses/:id/assignments/:assignment_id/submissions/update_grades
  grade_data[student_id_1][posted_grade]=90
  grade_data[student_id_2][posted_grade]=85
  grade_data[student_id_3][excuse]=true
```

Returns a Progress object; poll `GET /progress/:id` for completion.

### Grade Posting / Hiding (New Gradebook)

```
POST /courses/:id/assignments/:assignment_id/submissions/bulk_update
  # For manual posting policy
  assignment[post_manually]=true
```

### SpeedGrader

There is no direct SpeedGrader API. SpeedGrader is a UI feature. However, you can construct a SpeedGrader URL:

```
https://<canvas>/courses/:course_id/gradebook/speed_grader?assignment_id=:id&student_id=:user_id
```

All grading operations (scores, rubric assessments, comments) go through the submissions API.

### Submission Comments

```
PUT /courses/:id/assignments/:assignment_id/submissions/:user_id
  comment[text_comment]=Please revise your hypothesis tree
  comment[group_comment]=true                  # Post to all group members
```

---

## 16. Users, Enrollments, Sections, Groups

### List Course Users

```
GET /courses/:id/users
  enrollment_type[]=student
  search_term=Smith
  include[]=email
  include[]=enrollments
  include[]=avatar_url
```

### Enrollments

```
# List all enrollments in a course
GET /courses/:id/enrollments
  type[]=StudentEnrollment
  state[]=active

# List enrollments in a section
GET /sections/:section_id/enrollments

# Enroll a user
POST /courses/:id/enrollments
  enrollment[user_id]=USER_ID
  enrollment[type]=StudentEnrollment
  enrollment[enrollment_state]=active

# Remove/conclude enrollment
DELETE /courses/:id/enrollments/:enrollment_id
  task=conclude                                # "conclude", "deactivate", "delete"
```

### Sections

```
GET  /courses/:id/sections                     # List sections
POST /courses/:id/sections                     # Create section
  course_section[name]=Section 001
GET  /sections/:id                             # Get section details
PUT  /sections/:id                             # Update section
POST /sections/:id/crosslist/:new_course_id    # Cross-list
```

### Groups and Group Categories

```
# List group categories (group sets)
GET /courses/:id/group_categories

# Create a group set
POST /courses/:id/group_categories
  name=Project Teams
  self_signup=null                             # null, "enabled", "restricted"
  group_limit=4

# List groups in a set
GET /group_categories/:id/groups

# Create a group
POST /group_categories/:id/groups
  name=Team Alpha

# Add member to group
POST /groups/:group_id/memberships
  user_id=STUDENT_ID

# List group members
GET /groups/:group_id/users
```

---

## 17. Outcomes

### Outcome CRUD

```
GET  /outcomes/:id                             # Get outcome
PUT  /outcomes/:id                             # Update outcome
  title=MECE Framework Application
  description=Students can decompose problems into MECE components
  mastery_points=3
  ratings[0][description]=Exceeds
  ratings[0][points]=4
  ratings[1][description]=Meets
  ratings[1][points]=3
  ratings[2][description]=Approaching
  ratings[2][points]=2
  ratings[3][description]=Below
  ratings[3][points]=1
  calculation_method=decaying_average          # weighted_average, decaying_average, n_mastery, latest, highest, average
```

### Outcome Groups

```
# Get root outcome group for a course
GET /courses/:id/root_outcome_group

# Create subgroup
POST /courses/:id/outcome_groups/:group_id/subgroups
  title=Think Clearly Outcomes

# Link an outcome to a group
POST /courses/:id/outcome_groups/:group_id/outcomes
  outcome_id=EXISTING_OUTCOME_ID
  # OR create inline:
  title=New Outcome
  mastery_points=3
  ratings[0][description]=Exceeds
  ratings[0][points]=4

# Import outcomes from another group
POST /courses/:id/outcome_groups/:group_id/import
  source_outcome_group_id=SOURCE_GROUP_ID
```

### Outcome Alignments

```
GET /courses/:id/outcome_alignments
  student_id=USER_ID
  assignment_id=ASSIGNMENT_ID
```

---

## 18. Blueprint Courses

Blueprint courses let you maintain a "master" course and sync changes to associated sections. **Requires admin to enable.**

| Action | Method | Endpoint |
|--------|--------|----------|
| Get template | `GET` | `/courses/:id/blueprint_templates/default` |
| Update associations | `PUT` | `/courses/:id/blueprint_templates/default/update_associations` |
| List associated courses | `GET` | `/courses/:id/blueprint_templates/default/associated_courses` |
| Begin sync | `POST` | `/courses/:id/blueprint_templates/default/migrations` |
| List migrations | `GET` | `/courses/:id/blueprint_templates/default/migrations` |
| Migration details | `GET` | `/courses/:id/blueprint_templates/default/migrations/:id/details` |
| Unsynced changes | `GET` | `/courses/:id/blueprint_templates/default/unsynced_changes` |
| Lock/unlock object | `PUT` | `/courses/:id/blueprint_templates/default/restrict_item` |

### Lock a Specific Object

```
PUT /courses/:id/blueprint_templates/default/restrict_item
  content_type=assignment                      # assignment, attachment, discussion_topic, quiz, wiki_page
  content_id=456
  restricted=true
```

### Trigger a Sync

```
POST /courses/:id/blueprint_templates/default/migrations
  comment=Updated Week 8 content
  copy_settings=true                           # Include course settings
```

---

## 19. Content Migrations and Exports

### Import Content from Another Course

```
POST /courses/:dest_course_id/content_migrations
  migration_type=course_copy_importer
  settings[source_course_id]=SOURCE_COURSE_ID
```

### Import a Common Cartridge / IMS Package

```
POST /courses/:id/content_migrations
  migration_type=common_cartridge_importer
  # Then upload the file using the pre_attachment workflow
```

### Import a Moodle Backup

```
POST /courses/:id/content_migrations
  migration_type=moodle_converter
```

### Selective Import

```
POST /courses/:id/content_migrations
  migration_type=course_copy_importer
  settings[source_course_id]=123
  selective_import=true                        # Pauses at "waiting_for_select" state

# Then get available content:
GET /courses/:id/content_migrations/:migration_id/selective_data

# Then update with selections:
PUT /courses/:id/content_migrations/:migration_id
  selective_data[assignments][]=456
  selective_data[modules][]=789
```

### Date Shifting

```
date_shift_options[shift_dates]=true
date_shift_options[old_start_date]=2025-09-01
date_shift_options[old_end_date]=2025-12-15
date_shift_options[new_start_date]=2026-01-12
date_shift_options[new_end_date]=2026-04-22
```

### Export Course Content

```
POST /courses/:id/content_exports
  export_type=common_cartridge               # common_cartridge, qti, zip
  # Selective:
  select[modules][]=123
  select[assignments][]=456
```

### Available Migration Types

```
GET /courses/:id/content_migrations/migrators
```

Returns: `canvas_cartridge_importer`, `common_cartridge_importer`, `course_copy_importer`, `zip_file_importer`, `qti_converter`, `moodle_converter`

---

## 20. Analytics

### Course-Level

```
GET /courses/:id/analytics/activity            # Page views & participation by day
GET /courses/:id/analytics/assignments         # Assignment-level stats (min, max, median, etc.)
GET /courses/:id/analytics/student_summaries   # Per-student summary (page views, participation, tardiness)
```

### Per-Student

```
GET /courses/:id/analytics/users/:student_id/activity
GET /courses/:id/analytics/users/:student_id/assignments
GET /courses/:id/analytics/users/:student_id/communication
```

---

## 21. Conversations / Messaging

| Action | Method | Endpoint |
|--------|--------|----------|
| List conversations | `GET` | `/conversations` |
| Create conversation | `POST` | `/conversations` |
| Get conversation | `GET` | `/conversations/:id` |
| Add message | `POST` | `/conversations/:id/add_message` |
| Unread count | `GET` | `/conversations/unread_count` |
| Mark all read | `POST` | `/conversations/mark_all_as_read` |

### Send a Message to Students

```
POST /conversations
  recipients[]=course_12345_students           # All students in course
  subject=Important: Project Deadline Extended
  body=<p>The deadline for the consulting proposal has been extended to...</p>
  group_conversation=true                      # One conversation, all recipients
  force_new=true                               # Start new thread
  context_code=course_12345
  mode=async                                   # Use async for bulk messaging
```

### Recipient Shortcuts

- `course_12345` -- everyone in the course
- `course_12345_students` -- all students
- `course_12345_teachers` -- all teachers
- `section_101` -- all in section
- Individual user IDs

---

## The GraphQL API

Canvas also offers a GraphQL API at `POST /api/graphql`.

### Key Differences from REST

- **Single endpoint**: All queries go to `/api/graphql`
- **Request only what you need**: Specify exact fields, reducing over-fetching
- **Nested queries**: Fetch a course, its modules, and their items in one request
- **Relay-style pagination**: Uses cursor-based pagination with `first`, `after`, `pageInfo`

### Authentication

Same as REST: `Authorization: Bearer <TOKEN>`

### Example Query

```graphql
query {
  course(id: "12345") {
    name
    modulesConnection(first: 10) {
      nodes {
        name
        position
        moduleItems {
          title
          type
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
```

### GraphiQL Explorer

Visit `https://<your-canvas>/graphiql` to explore available queries and mutations interactively.

### Limitations

- GraphQL does **not** cover everything the REST API does -- fields are added incrementally
- Mutations (write operations) are more limited than REST
- For course creation and most write operations, REST is still required
- Best used for **reading** complex nested data efficiently

---

## Webhooks and Canvas Data

### Canvas Live Events (Webhooks)

Canvas can push real-time events to an external endpoint via **Live Events** (requires admin setup):

- Subscription-based: events for submissions, grades, logins, enrollments, etc.
- Uses **Caliper** or **Canvas-native** event format
- Delivered via HTTPS POST or AWS SQS

**Setup**: Requires Canvas admin to configure via `POST /api/lti/subscriptions` (LTI Advantage). Not something a professor can set up independently.

### Canvas Data 2

A data warehouse service providing:
- Historical data dumps (incremental and full)
- Database tables for enrollments, submissions, page views, etc.
- Accessible via DAP (Data Access Platform) API

**Access**: Requires institutional admin. Not available to individual professors.

### Practical Alternative for Professors

Instead of webhooks, poll the API periodically:
- Check `GET /courses/:id/assignments/:assignment_id/submission_summary` for submission counts
- Monitor `GET /courses/:id/analytics/student_summaries` for engagement
- Use `GET /courses/:id/enrollments?state[]=active` for roster changes

---

## Notable Limitations

### Things You CANNOT Do via the API

1. **New Quizzes content**: Cannot create/edit quiz questions, configure settings, or manage item banks (LTI boundary)
2. **SpeedGrader**: No API; it is purely a UI tool (grade via submissions API instead)
3. **Rich Content Editor templates**: No API for managing RCE templates
4. **Course card images via settings**: Must use `course[image_id]` or `course[image_url]` on the course update endpoint
5. **Student-facing UI customization**: Cannot control the Canvas theme, colors, or CSS from a course-level API
6. **Drag-and-drop reordering**: Must set `position` on each item individually
7. **Conditional release / Mastery Paths**: Limited API; must configure rules via UI
8. **Grade passback to SIS**: Requires admin-configured SIS integration, not a professor-level API action
9. **Attendance tool**: The Roll Call Attendance tool is an LTI app with no public API
10. **Analytics dashboards**: You can pull data but not create custom dashboards within Canvas
11. **Notifications**: You cannot configure a student's notification preferences; only send messages via Conversations or Announcements
12. **Home page layout**: You can set `default_view` (modules, syllabus, etc.) but cannot create a custom dashboard layout via API
13. **Course navigation tab icons**: Cannot customize tab icons, only show/hide/reorder
14. **Collaborative tools**: Google Docs, Microsoft integrations, etc. are LTI apps outside the API boundary
15. **Blueprint lock UI granularity**: API locks entire objects, not specific fields within an object

### HTML Sanitization

When posting HTML content (pages, assignments, syllabus), Canvas strips:
- `<script>` tags
- `<iframe>` tags (except whitelisted domains like YouTube, Vimeo)
- `on*` event handlers
- `javascript:` URLs
- Some CSS properties

Safe to use: standard HTML tags, inline styles (most properties), `<table>`, `<img>` with src, `<a>` tags, `<video>`/`<audio>` with whitelisted sources.

### Practical Tips

1. **Always store IDs**: When you create objects, save the returned IDs -- you will need them for module items, overrides, and associations
2. **Build in order**: Create assignment groups first, then assignments, then modules, then module items (which reference the assignments)
3. **Use `?per_page=100`**: Reduce pagination overhead for bulk reads
4. **Batch where possible**: Use bulk update endpoints for dates and grades
5. **Test with a sandbox course**: Create a development/test course to experiment before touching a live course
6. **Check `preview_html`**: Validate your HTML content before posting to pages or assignments
7. **Idempotency**: The API does not enforce idempotency -- running a create script twice will create duplicates. Build checks into your scripts.
