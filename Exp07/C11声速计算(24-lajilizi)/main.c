#include <stdio.h>
#include <math.h>
long double TheoremSonicVelocity(double temperature);
double RDelta(double determine,double theorem);
double AverageFDMethod(long double *L);

typedef struct{
    long double distance;
    int time;
}TimeInterval;
int main() {
    //读取原始数据
    FILE *datap;
    datap = fopen("OriginalData.txt","r");
    rewind(datap);
    double TemperatureCelcius[4]={0,0,0,0};
    long double Frequency[3]={0,0,0};
    long double L[3][10]={0};
    TimeInterval L4[10];
    for(int i=0;i<3;i++){
        fscanf(datap,"%lf",TemperatureCelcius+i);
        fscanf(datap,"%Lf",Frequency+i);
        for(int j=0;j<10;j++){
            fscanf(datap,"%Lf",L[i]+j);
        }
    }
    fscanf(datap,"%lf",&TemperatureCelcius[3]);
    for(int j=0;j<10;j++){
        fscanf(datap,"%Lf",&L4[j].distance);
    }
    for(int j=0;j<10;j++){
        fscanf(datap,"%d",&L4[j].time);
    }
    fclose(datap);
    //计算
    long double theorem_velocity[4]={0};
    long double wave_length[3]={0};
    long double velocity[4]={0};
    double delta[4]={0};
    wave_length[0] = AverageFDMethod(L[0])*2;
    wave_length[1] = AverageFDMethod(L[1])*2;
    wave_length[2] = AverageFDMethod(L[2]);
    for(int i=0;i<3;i++){
        velocity[i] = Frequency[i]*wave_length[i];
        theorem_velocity[i] = TheoremSonicVelocity(TemperatureCelcius[i]);
    }
    long double time_interval_velocity[9]={0};
    for(int j=0;j<9;j++){
        time_interval_velocity[j] = 1000*(L4[j].distance-L4[j+1].distance)/(L4[j].time-L4[j+1].time);
        velocity[3] = velocity[3] + time_interval_velocity[j];
    }
    velocity[3] = velocity[3]/9;
    theorem_velocity[3] = TheoremSonicVelocity(TemperatureCelcius[3]);
    for(int i=0;i<4;i++){
        delta[i] = RDelta(velocity[i],theorem_velocity[i]);
    }
    //写入
    FILE *resultp;
    resultp = fopen("result.txt","w+");
    fprintf(resultp,"驻波法\n");
    fprintf(resultp,"波长%Lf mm,波速%Lf m/s,理论波速%Lf m/s,相对误差%lf\n",wave_length[0],velocity[0],theorem_velocity[0],delta[0]);
    fprintf(resultp,"相位比较法\n");
    fprintf(resultp,"波长%Lf mm,波速%Lf m/s,理论波速%Lf m/s,相对误差%lf\n",wave_length[1],velocity[1],theorem_velocity[1],delta[1]);
    fprintf(resultp,"波形移动法\n");
    fprintf(resultp,"波长%Lf mm,波速%Lf m/s,理论波速%Lf m/s,相对误差%lf\n",wave_length[2],velocity[2],theorem_velocity[2],delta[2]);
    fprintf(resultp,"时差法\n");
    fprintf(resultp,"波速%Lf m/s,理论波速%Lf m/s,相对误差%lf\n",velocity[3],theorem_velocity[3],delta[0]);
    fclose(resultp);
    return 0;
}
//计算理论声速，温度摄氏度，速度m/s
long double TheoremSonicVelocity(double temperature){
    long double v = 331.45* sqrt(1+ temperature/273.15);
    return v;
}
//相对误差
double RDelta(double determine,double theorem){
    double delta = (determine - theorem)/theorem;
    return fabs(delta);
}
//逐差法计算中间量，在驻波和相位比较中为半波长，波形移动中为全波长，单位mm
//警告:该函数默认l值依次递减，若为依次递增，自行用注释修改
/*double AverageFDMethod(long double *L){
    long double sum = 0;
    for(int i=0;i<5;i++){
        sum = sum - *(L+i);
    }
    for(int i=5;i<10;i++){
        sum = sum + *(L+i);
    }
    sum = sum/25;
    return sum;
}*/
double AverageFDMethod(long double *L){
    long double sum = 0;
    for(int i=0;i<5;i++){
        sum = sum + *(L+i);
    }
    for(int i=5;i<10;i++){
        sum = sum - *(L+i);
    }
    sum = sum/25;
    return sum;
}

