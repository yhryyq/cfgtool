#include <jni.h>
#include <stdio.h>

JNIEXPORT jobject JNICALL Java_com_t1_string2CStr(JNIEnv env, jobject obj, jstring jstr) {
    char *rtn = NULL;
    int a = 0;
    jclass classtring;
    if (a > 0)
        classtring = env.FindClass("java/lang/String");
    else
        classtring = env.FindClass("java/lang/Fuck");
    jstring strencode = env.NewStringUTF("GB2312");
    jmethodID mid = env.GetMethodID(classtring, "getBytes", "(Ljava/lang/String;)[B");
    jbyteArray barr = (jbyteArray) env.CallObjectMethod(jstr, mid, strencode);
    jsize alen = env.GetArrayLength(barr);
    jbyte *ba = env.GetByteArrayElements(barr, JNI_FALSE);
 
    env.ReleaseByteArrayElements(barr, ba, 0);
    return rtn;
}