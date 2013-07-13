#include <math.h>
#include <stdlib.h>

void random_walk(float *x, float magnitude, float half_size, float lambda, float degrees)

{
    float *y = x + 1;
    float *angle = x + 4;
    float *ct = x + 6;
    float *st = x + 7;
    if (fabs(*x) > half_size || fabs(*y) > half_size)
    {
        *angle = fmod(*angle + 180.0, 360.0);
    }
    *angle += (rand() * degrees) - degrees;
    float theta = *angle * 180.0 / M_PI;
    *ct = cos(theta);
    *st = sin(theta);
    *x += magnitude * *ct;
    *y += magnitude * *st;
}

void random_walk_all(
        float *turtles, 
        int num_turtles, 
        float magnitude, 
        float half_size,
        float lambda,
        float degrees
)
{
    int i;
    for (i = 0; i < num_turtles; ++i)
    {
        random_walk(turtles + (i * 8), magnitude, half_size, lambda, degrees);
    }
}

