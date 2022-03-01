user_txt = '''
#include "canopen_eod_demo.h"
#include <runtime/canopen_types.h>
#include <runtime/apis.h>



#define OD_PARAM_INIT  {
	/*OD_PARAM_INIT*/
}

typedef struct 
{
	/*typedef struct*/
}od_t;

static const od_t od_default_data = OD_PARAM_INIT;

static od_t od;

/*OBJECT DICTIONARY*/

/**************************************************************************/
/* Declaration of pointed variables 第一个元素必须是空                     */
/**************************************************************************/
static const indextable SlaveApp_objdict[] = 
{
	/*indextable*/
};

const static indextable * SlaveApp_scanIndexExternOD (uint16_t wIndex, uint32_t * errorCode, ODCallback_t **callbacks)
{
	int i;
	*callbacks = NULL;
	switch(wIndex){
/*scan index od*/
		default:
			*errorCode = OD_NO_SUCH_OBJECT;
			return NULL;
	}
	*errorCode = OD_SUCCESSFUL;
	return &SlaveApp_objdict[i];
}



static quick_index  firstExternIndex = {
	/*quick first*/
};
static quick_index  lastExternIndex = {
	/*quick last*/
};

//  const static uint16_t SlaveApp_ObjdictSize = sizeof(SlaveApp_objdict)/sizeof(SlaveApp_objdict[0]);

/**
 * @brief 将本地字典数组地址和长度发送出去
 * 
 * @param len 
 * @return indextable* 
 */
static indextable * sendObjectInfo(uint16_t * len)
{
	*len = sizeof(SlaveApp_objdict)/sizeof(indextable);

	return &SlaveApp_objdict[0];
}

/**
 * @brief 恢复user的默认值
 * 
 */
static void ObjDictRestoreuserDefaultParam(void)
{
	RT_CALL(libc.memcpy)(&od,&od_default_data,sizeof(od));
}


void enableExternOD(void)
{
	RT_CALL(canopen.dict.set_op_method)(SlaveApp_scanIndexExternOD,sendObjectInfo,ObjDictRestoreuserDefaultParam,firstExternIndex,lastExternIndex);
}















'''