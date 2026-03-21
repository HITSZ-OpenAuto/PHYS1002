#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define G 0.0097887
#undef G
double Theorem_h0(double x0,double m1,double m2,double y);
double Average_x(double* x);
double LostEkProportion1(double m1,double m2,double h0,double y,double x);
double LostEkProportion2(double actual_h,double altitude_h,double h0);

//被撞球属性
typedef struct {
    double mass;
    double diameter;
    double theorem_h0; //高度差
    double altitude_h; //设置高度h=h0+r+y
    double x_average;
    double proportion1;
    double proportion2;
}TestantProperty;
int main() {
    //读取数据并计算h0
    FILE *datap = fopen("OriginalData.txt","r");
    rewind(datap);
    double pillar_height_y = 0;
    double preset_x0 = 0;
    double oscillation_mass = 0;
    fscanf(datap,"%lf",&pillar_height_y);
    fscanf(datap,"%lf",&preset_x0);
    fscanf(datap,"%lf",&oscillation_mass);
    TestantProperty balls[3]={0};
    for(int i=0;i<3;i++){
        fscanf(datap,"%lf",&balls[i].mass);
        fscanf(datap,"%lf",&balls[i].diameter);
        balls[i].theorem_h0 = Theorem_h0(preset_x0,oscillation_mass,balls[i].mass,pillar_height_y);
        balls[i].altitude_h = balls[i].theorem_h0 + pillar_height_y + balls[i].diameter/2;
    }
    double x[3][10] = {0};
    double actual_altitude_h[3] = {0};
    for(int i=0;i<3;i++){
        for(int j=0;j<10;j++){
            fscanf(datap,"%lf",&x[i][j]);
        }
        fscanf(datap,"%lf",&actual_altitude_h[i]);
    }
    fclose(datap);
    //计算
    for(int i=0;i<3;i++){
        balls[i].x_average = Average_x(x[i]);
        balls[i].proportion1 = LostEkProportion1(oscillation_mass,balls[i].mass,balls[i].theorem_h0,pillar_height_y,balls[i].x_average);
        balls[i].proportion2 = LostEkProportion2(actual_altitude_h[i],balls[i].altitude_h,balls[i].theorem_h0);
    }
    //写入
    FILE *resultp = fopen("results.txt","w+");
    if(resultp==NULL)
        exit(1);
    fprintf(resultp,"被碰球球属性\n");
    for(int i=0;i<3;i++){
        fprintf(resultp,"球%d应设置高度差h0=%.2lf cm,摆球设置高度h=%.2lf cm\n",i+1,balls[i].theorem_h0,balls[i].altitude_h);
    }
    fprintf(resultp,"被碰球球的平均落点位置\n");
    for(int i=0;i<3;i++){
        fprintf(resultp,"球%d平均落点位置x=%.2lf cm\n",i+1,balls[i].x_average);
    }
    fprintf(resultp,"使用平均位置计算损失能量比\n");
    for(int i=0;i<3;i++){
        fprintf(resultp,"球%d  %.4lf\n",i+1,balls[i].proportion1);
    }
    fprintf(resultp,"使用实际所需高度计算损失能量比\n");
    for(int i=0;i<3;i++){
        fprintf(resultp,"球%d  %.4lf\n",i+1,balls[i].proportion2);
    }
    fclose(resultp);
    return 0;
}
//计算理论应设定的高度差h0
double Theorem_h0(double x0,double m1,double m2,double y){
    double h0= x0*x0*(m1+m2)*(m1+m2)/(16*m1*m1*y);
    return h0;
}
//计算x的均值
double Average_x(double* x){
    double sum = 0;
    for(int i=0;i<10;i++){
        sum = sum + *(x+i);
    }
    return sum/10;
}
//利用x的均值计算损失机械能占比
double LostEkProportion1(double m1,double m2,double h0,double y,double x){
    double twice_lost = m2*x*(2* sqrt(h0/y)-(m1+m2)*x/(2*m1*y));
    double twice_original = 2*m1*h0;
    return twice_lost/twice_original;
}
//利用实际打靶所需高度计算损失机械能占比
double LostEkProportion2(double actual_h,double altitude_h,double h0){
    double lost = actual_h - altitude_h;
    return lost/(h0+lost);
}