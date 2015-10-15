varlist1 <- names(cnema35_chris)[27:36]
varlist2 <- names(cnema35_chris)[63:72]
var=rbind(varlist1,varlist2)
tc = trainControl("cv",10, savePredictions = T)

cnema35_chris$win_01 = as.factor(cnema35_chris$win_01)

models <- apply(var,2, function(x) {
  train(formula(substitute(as.factor(win_01)~p+j, list(p = as.name(x[1]),j=as.name(x[2])))),
        data=cnema35_chris,method="glm",trControl=tc,family=binomial(link="logit"))
})



models <- apply(var,2, function(x) {
  glm(substitute(win_01~p+j, list(p = as.name(x[1]),j=as.name(x[2]))),family=binomial(logit),
      data=cnema35_chris)
})