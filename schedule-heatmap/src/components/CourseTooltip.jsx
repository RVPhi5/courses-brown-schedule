import PropTypes from 'prop-types';
import './CourseTooltip.css';

function CourseTooltip({ courses, position, visible }) {
    if (!visible || !courses || courses.length === 0) {
        return null;
    }

    // Sort courses by enrollment (descending)
    const sortedCourses = [...courses].sort((a, b) =>
        (b.current_enrollment || 0) - (a.current_enrollment || 0)
    );

    return (
        <div
            className="course-tooltip"
            style={{
                top: position.top,
                left: position.left,
            }}
        >
            <div className="tooltip-header">
                <strong>{courses.length}</strong> course{courses.length !== 1 ? 's' : ''} at this time
            </div>
            <div className="tooltip-courses">
                {sortedCourses.map((course, index) => (
                    <div key={`${course.code}-${course.section}-${index}`} className="tooltip-course">
                        <div className="course-code-name">
                            <span className="course-code">{course.code}</span>
                            <span className="course-name">{course.name}</span>
                        </div>
                        <div className="course-details">
                            <span className="course-instructor">{course.instructor}</span>
                            <span className="course-enrollment">
                                {course.current_enrollment}/{course.max_enrollment} students
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

CourseTooltip.propTypes = {
    courses: PropTypes.arrayOf(PropTypes.shape({
        code: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        instructor: PropTypes.string,
        current_enrollment: PropTypes.number,
        max_enrollment: PropTypes.number,
        section: PropTypes.string,
    })),
    position: PropTypes.shape({
        top: PropTypes.number,
        left: PropTypes.number,
    }),
    visible: PropTypes.bool.isRequired,
};

export default CourseTooltip;
