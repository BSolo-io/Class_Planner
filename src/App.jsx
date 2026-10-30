import { useState } from "react";
import "./App.css";
import { COURSES, DEGREES } from "./lib/catalog";
import { nextSemester, parseCompleted, progress } from "./lib/prereqs";

const HERO_PREVIEW_CODES = ["ENG 1101", "MAT 1275", "CSCI 1111"];

function App() {
  const [page, setPage] = useState("home");

  const [student, setStudent] = useState({
    name: "",
    email: "",
    major: "",
    year: "",
    interests: "",
    career: "",
    completed: "",
  });

  const updateStudent = (e) => {
    setStudent({
      ...student,
      [e.target.name]: e.target.value,
    });
  };

  const submitProfile = (e) => {
    e.preventDefault();
    setPage("dashboard");
  };

  const selectedDegree = DEGREES.find((d) => d.id === student.major) ?? null;
  const completedCodes = parseCompleted(student.completed, COURSES);
  const completedSet = new Set(completedCodes);

  const associateDegrees = DEGREES.filter((d) => d.kind === "AAS" || d.kind === "AS");
  const bachelorDegrees = DEGREES.filter((d) => d.kind !== "AAS" && d.kind !== "AS");

  const plan = selectedDegree ? nextSemester(selectedDegree, completedSet, COURSES) : null;
  const planProgress = selectedDegree ? progress(selectedDegree, completedSet, COURSES) : null;
  const heroPreview = HERO_PREVIEW_CODES.map((code) => COURSES[code]).filter(Boolean);

  return (
    <div className="app">

      {/* NAVIGATION */}
      <nav className="navbar">
        <div className="brand">
          <span className="brand-icon">C</span>
          <span>
            Class<span className="brand-light">Match</span>
          </span>
        </div>

        <div className="nav-links">
          <button onClick={() => setPage("home")}>
            Home
          </button>

          <button onClick={() => setPage("profile")}>
            My Profile
          </button>

          <button onClick={() => setPage("dashboard")}>
            Course Planner
          </button>
        </div>

        <button
          className="nav-cta"
          onClick={() => setPage("profile")}
        >
          Get Started
        </button>
      </nav>

      {/* HOME PAGE */}
      {page === "home" && (
        <main>
          <section className="hero">

            <div className="hero-content">
              <span className="eyebrow">
                YOUR ACADEMIC JOURNEY STARTS HERE
              </span>

              <h1>
                Plan smarter.
                <br />
                <span>Graduate stronger.</span>
              </h1>

              <p>
                A personalized course matching experience designed
                to help City Tech students organize their
                academic journey and find courses that match
                their academic goals.
              </p>

              <button
                className="primary-btn"
                onClick={() => setPage("profile")}
              >
                Create My Academic Plan →
              </button>

              <div className="hero-note">
                Designed for City Tech students
              </div>
            </div>

            <div className="hero-visual">
              <div className="visual-card">

                <div className="visual-top">
                  <span>MY ACADEMIC PLAN</span>
                  <span className="status">● PLANNING</span>
                </div>

                <h3>Your next semester</h3>

                <div className="visual-stat">
                  <div>
                    <strong>{heroPreview.length}</strong>
                    <span>Suggested courses</span>
                  </div>

                  <div>
                    <strong>{heroPreview.reduce((sum, c) => sum + c.credits, 0)}</strong>
                    <span>Credit hours</span>
                  </div>
                </div>

                {heroPreview.map((course) => (
                  <div
                    className="visual-course"
                    key={course.code}
                  >
                    <span className="course-dot"></span>

                    <div>
                      <strong>{course.title}</strong>
                      <small>{course.code}</small>
                    </div>

                    <span>{course.credits} credits</span>
                  </div>
                ))}

                <div className="visual-footer">
                  A clearer path to your goals.
                </div>
              </div>

              <div className="floating-label">
                ✦ Your future, organized
              </div>
            </div>

          </section>

          {/* FEATURES */}
          <section className="features">
            <div className="section-heading">
              <span className="eyebrow">HOW IT WORKS</span>
              <h2>Your academic journey, simplified.</h2>
            </div>

            <div className="feature-grid">

              <div className="feature-card">
                <h3>01. Build Your Profile</h3>
                <p>
                  Enter your major, academic year, interests,
                  and future career goals.
                </p>
              </div>

              <div className="feature-card">
                <h3>02. Discover Courses</h3>
                <p>
                  Explore course suggestions based on your
                  academic interests.
                </p>
              </div>

              <div className="feature-card">
                <h3>03. Plan Your Future</h3>
                <p>
                  Organize your academic journey and
                  explore your next semester.
                </p>
              </div>

            </div>
          </section>
        </main>
      )}

      {/* STUDENT PROFILE PAGE */}
      {page === "profile" && (
        <main className="form-page">

          <div className="form-intro">
            <span className="eyebrow">GET STARTED</span>

            <h1>Build your student profile.</h1>

            <p>
              Tell us about yourself so we can help organize
              your academic journey.
            </p>
          </div>

          <form
            className="profile-form"
            onSubmit={submitProfile}
          >
            <h2>Student information</h2>

            <div className="form-grid">
              <label>
                Full Name

                <input
                  type="text"
                  name="name"
                  placeholder="Enter your name"
                  value={student.name}
                  onChange={updateStudent}
                  required
                />
              </label>

              <label>
                Student Email

                <input
                  type="email"
                  name="email"
                  placeholder="Enter your student email"
                  value={student.email}
                  onChange={updateStudent}
                  required
                />
              </label>

              <label>
                Degree

                <select
                  name="major"
                  value={student.major}
                  onChange={updateStudent}
                  required
                >
                  <option value="">Select your degree</option>
                  <optgroup label="Associate's Degrees">
                    {associateDegrees.map((d) => (
                      <option key={d.id} value={d.id}>{d.degree}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Bachelor's Degrees">
                    {bachelorDegrees.map((d) => (
                      <option key={d.id} value={d.id}>{d.degree}</option>
                    ))}
                  </optgroup>
                </select>
              </label>

              <label>
                Academic Year

                <select
                  name="year"
                  value={student.year}
                  onChange={updateStudent}
                  required
                >
                  <option value="">Select your year</option>
                  <option value="Freshman">Freshman</option>
                  <option value="Sophomore">Sophomore</option>
                  <option value="Junior">Junior</option>
                  <option value="Senior">Senior</option>
                </select>
              </label>
            </div>

            <div className="form-divider" />

            <label>
              Academic Interests

              <textarea
                name="interests"
                placeholder="What subjects are you interested in?"
                value={student.interests}
                onChange={updateStudent}
              />
            </label>

            <label>
              Future Career Goals

              <input
                type="text"
                name="career"
                placeholder="Example: Software Engineer"
                value={student.career}
                onChange={updateStudent}
              />
            </label>

            <label>
              Previously Completed Courses

              <textarea
                name="completed"
                placeholder="Course codes, separated by commas or new lines. Example: ENG 1101, MAT 1275, ACC 1101"
                value={student.completed}
                onChange={updateStudent}
              />
            </label>

            <button
              className="primary-btn submit-btn"
              type="submit"
            >
              Find My Courses →
            </button>

          </form>
        </main>
      )}

      {/* COURSE PLANNER DASHBOARD */}
      {page === "dashboard" && (
        <main className="dashboard">

          <div className="dashboard-heading">
            <div>
              <span className="eyebrow">
                YOUR COURSE PLANNER
              </span>

              <h1>
                Welcome{student.name ? `, ${student.name}` : ""}!
              </h1>

              <p>
                {selectedDegree
                  ? "Here's a suggested next semester based on your degree and completed courses."
                  : "Pick a degree on your profile to see a customized plan."}
              </p>
            </div>

            <button
              className="outline-btn"
              onClick={() => setPage("profile")}
            >
              Edit My Profile
            </button>
          </div>

          {/* STUDENT INFORMATION */}
          <div className="student-summary">

            <div>
              <span>YOUR DEGREE</span>
              <strong>
                {selectedDegree?.degree || "Not selected"}
              </strong>
            </div>

            <div>
              <span>ACADEMIC YEAR</span>
              <strong>
                {student.year || "Not selected"}
              </strong>
            </div>

            <div>
              <span>CAREER GOAL</span>
              <strong>
                {student.career || "Not specified"}
              </strong>
            </div>

          </div>

          {selectedDegree ? (
            <>
              {/* SUGGESTED NEXT SEMESTER */}
              <div className="recommendation-heading">
                <h2>Suggested Next Semester</h2>
                <span className="sample-label">{plan.credits} CREDITS</span>
              </div>

              <div className="course-grid">
                {plan.courses.length === 0 && (
                  <p>
                    No open courses found - either everything required is
                    completed, or the next courses need a prerequisite first.
                  </p>
                )}

                {plan.courses.map((course) => (
                  <div
                    className="recommendation-card"
                    key={course.code}
                  >
                    <span className="course-type">
                      {course.group}
                    </span>

                    <h3>{course.title}</h3>

                    <p>{course.code}</p>

                    <div className="card-bottom">
                      <span>{course.credits} Credit Hours</span>
                      <span>{course.minGrade ? `Min grade ${course.minGrade}` : ""}</span>
                    </div>

                  </div>
                ))}

              </div>

              {/* PROGRESS */}
              <div className="planner-banner">
                <div>
                  <span className="eyebrow">PROGRESS</span>
                  <h2>{planProgress.creditsDone} of {planProgress.creditsNeeded} credits done</h2>
                  <p>
                    {planProgress.groups
                      .map((g) => `${g.name}: ${g.creditsEarned}/${g.creditsNeeded}`)
                      .join(" · ")}
                  </p>
                </div>
              </div>
            </>
          ) : (
            <button
              className="primary-btn"
              onClick={() => setPage("profile")}
            >
              Build My Profile →
            </button>
          )}

          <p className="disclaimer">
            This is a demo built on sample City Tech-style degree data, not the
            real catalog. It does not use the most optimal course order - just
            the next open courses. Confirm any real plan with an academic advisor.
          </p>

        </main>
      )}

      {/* FOOTER */}
      <footer className="footer">

        <div className="brand">
          <span className="brand-icon">C</span>
          <span>
            Class<span className="brand-light">Match</span>
          </span>
        </div>

        <p>
          Helping students plan their academic journey.
        </p>

        <span>© 2026 ClassMatch</span>

      </footer>

    </div>
  );
}

export default App;
