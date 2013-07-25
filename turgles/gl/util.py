from turgles.gl.api import (
    GL_BYTE,
    GL_SHORT,
    GL_UNSIGNED_BYTE,
    GL_UNSIGNED_SHORT,
    GL_UNSIGNED_INT,
    GL_FLOAT,
    GL_INT,
    GLbyte,
    GLshort,
    GLint,
    GLubyte,
    GLushort,
    GLuint,
    GLfloat,
)


GL_TYPEMAP = {
    GLbyte:   (GL_BYTE, 1),
    GLubyte:  (GL_UNSIGNED_BYTE, 1),
    GLshort:  (GL_SHORT, 2),
    GLushort: (GL_UNSIGNED_SHORT, 2),
    GLint:    (GL_INT, 4),
    GLuint:   (GL_UNSIGNED_INT, 4),
    GLfloat:  (GL_FLOAT, 4)
}
