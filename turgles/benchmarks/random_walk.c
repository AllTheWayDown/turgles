#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <sys/time.h>
#include <sys/resource.h>

const int N = 1000;

const double DEG2RAD = 3.1452 / 180;

double radians (double d) {
    return d * DEG2RAD;
}

double expon(double x)
{
  double z;                     // Uniform random number (0 < z < 1)
  double exp_value;             // Computed exponential value to be returned

  // Pull a uniform random number (0 < z < 1)
  do
  {
    z = rand();
  }
  while ((z == 0) || (z == 1));

  // Compute exponential random variable using inversion method
  exp_value = -x * log(z);

  return(exp_value);
}

double get_time()
{
    struct timeval t;
    gettimeofday(&t, NULL);
    return t.tv_sec + t.tv_usec*1e-6;
}

int main(int argc, char** argv)
{
    int world_size = 800;
    int half_size = 400;
    float degrees = 15.0;
    float turtles[N * 4];
    float lambd = 1.0 / degrees;

    for (int x = 0; x < N; ++x)
    {
        int y = x + 1;
        int angle = x + 2;
        turtles[x] = rand() * 400;
        turtles[y] = rand() * 400;
        turtles[angle] = rand() * 360;

    }

    double total = 0.0;
    float magnitude = 50.0 / 30.0;

    for (int i = 0; i < 1000; ++i)
    {
        double start = get_time();
        for (int x = 0; x < N; ++x)
        {
            int y = x + 1;
            int angle = x + 2;
            turtles[angle] += expon(degrees) - degrees;
            float theta = radians(turtles[angle]);
            float dy = magnitude * sin(theta);
            float dx = magnitude * cos(theta);
            turtles[x] += dx;
            turtles[y] += dy;

            if (turtles[x] > half_size)
                turtles[x] -= world_size;
            else if (turtles[x] < -half_size)
                turtles[x] += world_size;

            if (turtles[y] > half_size)
                turtles[y] -= world_size;
            else if (turtles[y] < -half_size)
                turtles[y] += world_size;
            //printf("%f, %f\n", turtles[x], turtles[y]);
        }

        double end = get_time();
        total += end - start;
    }
    printf("%f\n", total);
    return 0;
}

